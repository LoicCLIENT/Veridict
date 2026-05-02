// Caso Detail Components
export { default as Timeline, mockTimelineEvents } from "./Timeline";
export { default as TimelineEvent } from "./TimelineEvent";
export { default as ConfrontacionTab } from "./ConfrontacionTab";
export type { TimelineEventData, EventType } from "./TimelineEvent";

// Re-export reconstruction components for convenience
export {
  AccidentScene2D,
  mockSceneDataCaso1,
  mockSceneDataCaso2,
  mockSceneDataCaso3,
  getSceneDataByCaseId,
  type AccidentSceneData
} from "../reconstruction";
