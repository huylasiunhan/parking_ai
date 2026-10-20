from app.ml.geometry import ParkingSlot, calculate_ios, BoundingBox

from enum import StrEnum
from dataclasses import dataclass

class SlotStatus(StrEnum):
    EMPTY = "EMPTY"
    OCCUPIED = "OCCUPIED"

@dataclass(frozen=True)
class SlotOccupancyResult:
    slot_id : int
    status : SlotStatus
    confidence : float
    match_box : BoundingBox | None = None
    ios_ratio : float = 0.0 


class SlotStateTracker:
    def __init__(self, slot_id : int, current_status : SlotStatus = SlotStatus.EMPTY, candidate_status : SlotStatus = None):
        self.slot_id = slot_id
        self.current_status = current_status
        self.candidate_status = candidate_status
        self.consecutive_frames = 0
        

    def update(self, instant_status : SlotStatus, threshold_frame : int = 5) -> SlotStatus:
        if instant_status == self.current_status:
            self.candidate_status = self.current_status
            self.consecutive_frames = 0
            return self.current_status
        
        if instant_status == self.candidate_status:
            self.consecutive_frames += 1
            if self.consecutive_frames >= threshold_frame:
                self.current_status = instant_status
                self.candidate_status = None
                self.consecutive_frames = 0
                return self.current_status
            return self.current_status
        else:
            self.candidate_status = instant_status
            self.consecutive_frames = 1
            return self.current_status
            

            


class OccupancyEngine():
    def __init__(self, ios_threshold : float = 0.3):
        self.ios_threshold = ios_threshold
        self._trackers : dict[int, SlotStateTracker] = {}

    def compute_instantaneous_occupancy(self, slots : list[ParkingSlot], detections : list[BoundingBox]) -> list[SlotOccupancyResult]:
        result = []
        for slot in slots:
            best_ios = 0.0
            best_box = None
            for box in detections:
                ios = calculate_ios(box, slot)
                if ios > best_ios:
                    best_ios = ios 
                    best_box = box
            
            if best_ios >= self.ios_threshold and best_box is not None:
                result.append(SlotOccupancyResult(
                    slot_id= slot.id,
                    status= SlotStatus.OCCUPIED,
                    confidence= best_box.confidence,
                    match_box=best_box,
                    ios_ratio=best_ios
                ))
            else:
                result.append(SlotOccupancyResult(
                    slot_id= slot.id,
                    status= SlotStatus.EMPTY,
                    confidence= 1.0,
                    match_box=None,
                    ios_ratio=0.0
                ))
        return result

    def compute_smoothed_occupancy(self, slots : list[ParkingSlot], detections : list[BoundingBox], threshold_frame : int = 5) -> list[SlotOccupancyResult]:
        result = []
        instant_occupancy = self.compute_instantaneous_occupancy(slots, detections)
        for res in instant_occupancy:
            if res.slot_id not in self._trackers:
                self._trackers[res.slot_id] = SlotStateTracker(slot_id= res.slot_id, current_status= SlotStatus.EMPTY, candidate_status=res.status)
            self._trackers[res.slot_id].update(instant_status=res.status, threshold_frame=threshold_frame)
            result.append(SlotOccupancyResult(
                slot_id=res.slot_id,
                status=self._trackers[res.slot_id].current_status,
                confidence=res.confidence,
                match_box=res.match_box,
                ios_ratio=res.ios_ratio
            ))
        return result


        