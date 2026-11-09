# Rover Mapping & Navigation

2026 대한민국 우주로버 경진대회를 준비하며 개발한 로버의 **3D 매핑·위치 추정·경로 계획·주행 제어** 프로젝트입니다. 카메라와 관성 센서로 환경을 관측하고, 지형 지도에서 방문 지점과 경로를 구성해 시뮬레이션 및 실기 연동으로 이어지는 시스템을 구현했습니다.

## 주요 구현

- **3D 매핑**: Intel RealSense D435의 stereo·depth 수집, ORB-SLAM3 기반 시각 위치 추정, TSDF 지도 재구성과 지형·costmap 생성
- **센서 융합**: 영상·IMU·엔코더를 결합하는 ESKF 위치 추정과 시간 정렬 분석
- **경로 계획·제어**: STL 기반 임무 편집, MPPI 경로 계획, 경사로·장애물 구간의 주행과 복귀 로직
- **시뮬레이션**: Isaac Sim 기반 센서·물리 시뮬레이션, 추정 위치를 사용하는 폐루프 주행, RL residual 실험
- **실기 연동**: Raspberry Pi 수집·주행 스택, STM 제어 인터페이스, 수동 조종과 주행 상태 중계 화면

## 시스템 구성

```text
D435 · IMU · Encoder
        ↓
영상 위치 추정 · ESKF 센서 융합
        ↓
3D 지도 · 지형 분석 · Costmap
        ↓
임무 구성 · MPPI 경로 계획
        ↓
시뮬레이션 / Raspberry Pi · STM 실기 연동
```

| 디렉토리 | 내용 |
|---|---|
| `experiments/handheld_mapping` | 영상 수집, 지도 재구성, 지형 분석, 임무 계획 |
| `experiments/localization` | 센서 융합과 위치 추정 |
| `experiments/site_sim` | 물리 시뮬레이션과 주행 실험 |
| `deployment` | 실기 주행 스택과 중계 화면 |
| `ros2_ws`, `teleop` | ROS 2 adapter, 로버 모델, 제어 인터페이스 |
| `tests` | 매핑·위치 추정·주행 모듈의 회귀 테스트 |

**기술**: Python, C++, ROS 2, ORB-SLAM3, Open3D, Isaac Sim, NumPy, PyQt5

이 저장소는 프로젝트 구현을 소개하는 포트폴리오용 소스입니다. 시뮬레이션 결과와 실기 검증은 구분하며, 전체 자율 임무의 실기 완주나 위치 정확도를 보장하는 결과로 제시하지 않습니다. 원본 센서 데이터·실행 환경·대용량 실험 산출물은 포함하지 않습니다.

외부 프로젝트의 출처와 라이선스는 [third_party](third_party/README.md)에 정리되어 있습니다.
