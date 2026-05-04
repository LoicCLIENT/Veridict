import { AccidentSceneData } from "./AccidentScene2D";

// Mock data for Caso 1: Cambio de carril sin señalizar M-30
// Trajectories optimized for new larger viewBox centered on impact
export const mockSceneDataCaso1: AccidentSceneData = {
  road: {
    type: "straight",
    lanes: 4,
    laneWidth: 3.5,
    speedLimit: 50,
  },
  vehicleA: {
    // Vehicle A traveling on right lane (negative Y), approaching from left
    trajectory: [
      { x: -5, y: -5.5, time: 0, speed: 67 },
      { x: 8, y: -5.5, time: 0.5, speed: 67 },
      { x: 20, y: -5.5, time: 1.0, speed: 67 },
      { x: 32, y: -5.5, time: 1.5, speed: 67 },
      { x: 44, y: -5.5, time: 2.0, speed: 65 },
      { x: 54, y: -5.5, time: 2.5, speed: 60 },
      { x: 62, y: -5.5, time: 2.8, speed: 55 },
      { x: 70, y: -5.2, time: 3.0, speed: 50 },
      { x: 78, y: -4.8, time: 3.2, speed: 48 },
      { x: 85, y: -4.2, time: 3.4, speed: 45 },
      { x: 90, y: -3.5, time: 3.6, speed: 42 },
      { x: 95, y: -3, time: 3.8, speed: 38 },
      { x: 98, y: -2.8, time: 4.0, speed: 35 },
    ],
    brakeStartTime: 2.5,
    brakeDistance: 14,
    initialSpeed: 67,
    impactSpeed: 45.2,
  },
  vehicleB: {
    // Vehicle B on left lane (positive Y), changing lanes WITHOUT signaling
    trajectory: [
      { x: 15, y: 5.5, time: 0, speed: 55 },
      { x: 28, y: 5.5, time: 0.5, speed: 55 },
      { x: 40, y: 5.2, time: 1.0, speed: 55 },
      { x: 52, y: 4.5, time: 1.5, speed: 55 },
      { x: 62, y: 3, time: 2.0, speed: 55 },
      { x: 72, y: 1, time: 2.5, speed: 55 },
      { x: 80, y: -1, time: 3.0, speed: 55 },
      { x: 88, y: -2.2, time: 3.5, speed: 52 },
      { x: 94, y: -2.8, time: 3.8, speed: 50 },
      { x: 98, y: -3, time: 4.0, speed: 48 },
    ],
    brakeStartTime: 3.6,
    brakeDistance: 6,
    initialSpeed: 55,
    impactSpeed: 50.3,
  },
  impact: {
    x: 98,
    y: -3,
    time: 4.0,
    angle: 15,
    deltaV_A: 22.1,
    deltaV_B: 18.7,
  },
  metadata: {
    scaleMetersPerUnit: 1,
    weatherCondition: "Light rain",
    roadCondition: "Wet",
    visibility: "Good",
  },
};

// Mock data for Caso 2: Atropello en paso de cebra (pedestrian at crosswalk)
export const mockSceneDataCaso2: AccidentSceneData = {
  road: {
    type: "intersection",
    lanes: 2,
    laneWidth: 3.5,
    speedLimit: 30,
  },
  vehicleA: {
    // Vehicle approaching intersection, fails to stop for pedestrian
    trajectory: [
      { x: -10, y: 4, time: 0, speed: 52 },
      { x: 5, y: 4, time: 0.4, speed: 52 },
      { x: 18, y: 4, time: 0.8, speed: 52 },
      { x: 30, y: 4, time: 1.2, speed: 50 },
      { x: 40, y: 4, time: 1.6, speed: 48 },
      { x: 48, y: 4, time: 2.0, speed: 45 },
      { x: 55, y: 4, time: 2.3, speed: 40 },
      { x: 62, y: 4, time: 2.6, speed: 35 },
      { x: 68, y: 4, time: 2.9, speed: 30 },
      { x: 73, y: 4, time: 3.2, speed: 28 },
      { x: 78, y: 4, time: 3.5, speed: 25 },
    ],
    brakeStartTime: 2.3,
    brakeDistance: 18.5,
    initialSpeed: 52,
    impactSpeed: 28,
  },
  vehicleB: {
    // Pedestrian crossing at crosswalk
    trajectory: [
      { x: 75, y: 22, time: 0, speed: 5 },
      { x: 75, y: 19, time: 0.5, speed: 5 },
      { x: 75, y: 16, time: 1.0, speed: 5 },
      { x: 76, y: 13, time: 1.5, speed: 5 },
      { x: 76, y: 10, time: 2.0, speed: 5 },
      { x: 77, y: 8, time: 2.5, speed: 5 },
      { x: 77, y: 6, time: 3.0, speed: 4 },
      { x: 78, y: 5, time: 3.3, speed: 3 },
      { x: 78, y: 4, time: 3.5, speed: 0 },
    ],
    brakeStartTime: 99, // Pedestrian - no brake
    brakeDistance: 0,
    initialSpeed: 5,
    impactSpeed: 0,
  },
  impact: {
    x: 78,
    y: 4,
    time: 3.5,
    angle: 90,
    deltaV_A: 8,
    deltaV_B: 28,
  },
  metadata: {
    scaleMetersPerUnit: 1,
    weatherCondition: "Clear",
    roadCondition: "Dry",
    visibility: "Good",
  },
};

// Mock data for Caso 3: Alcance trasero A-6 (highway rear-end collision)
export const mockSceneDataCaso3: AccidentSceneData = {
  road: {
    type: "straight",
    lanes: 3,
    laneWidth: 3.75,
    speedLimit: 120,
  },
  vehicleA: {
    // Vehicle being hit from behind (slowing down due to traffic)
    trajectory: [
      { x: 25, y: -4, time: 0, speed: 100 },
      { x: 38, y: -4, time: 0.5, speed: 90 },
      { x: 48, y: -4, time: 1.0, speed: 75 },
      { x: 56, y: -4, time: 1.5, speed: 60 },
      { x: 62, y: -4, time: 2.0, speed: 45 },
      { x: 67, y: -4, time: 2.5, speed: 35 },
      { x: 72, y: -4, time: 3.0, speed: 28 },
      { x: 76, y: -4, time: 3.5, speed: 25 },
    ],
    brakeStartTime: 0.5,
    brakeDistance: 42,
    initialSpeed: 100,
    impactSpeed: 25,
  },
  vehicleB: {
    // Vehicle hitting from behind (distracted driver)
    trajectory: [
      { x: -10, y: -4, time: 0, speed: 110 },
      { x: 8, y: -4, time: 0.5, speed: 110 },
      { x: 25, y: -4, time: 1.0, speed: 110 },
      { x: 42, y: -4, time: 1.5, speed: 108 },
      { x: 55, y: -4, time: 2.0, speed: 100 },
      { x: 65, y: -4, time: 2.5, speed: 88 },
      { x: 72, y: -4, time: 3.0, speed: 75 },
      { x: 76, y: -4, time: 3.5, speed: 65 },
    ],
    brakeStartTime: 2.5,
    brakeDistance: 32,
    initialSpeed: 110,
    impactSpeed: 65,
  },
  impact: {
    x: 76,
    y: -4,
    time: 3.5,
    angle: 0,
    deltaV_A: 40,
    deltaV_B: 40,
  },
  metadata: {
    scaleMetersPerUnit: 1,
    weatherCondition: "Sunny",
    roadCondition: "Dry",
    visibility: "Excellent",
  },
};

// Helper to get scene data by case ID
export function getSceneDataByCaseId(caseId: string): AccidentSceneData {
  switch (caseId) {
    case "1":
      return mockSceneDataCaso1;
    case "2":
      return mockSceneDataCaso2;
    case "3":
      return mockSceneDataCaso3;
    default:
      return mockSceneDataCaso1;
  }
}
