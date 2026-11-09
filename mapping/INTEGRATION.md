# 매핑 코드 통합 안내

원본: [lee-robot-lab/ksrc-rover-challenge](https://github.com/lee-robot-lab/ksrc-rover-challenge), `main`, commit `e8e841fe0c9b09b7cee5a63b25acf8577de2d416`.

기존 `firmware/`, `pi/`, `ros/`, `sim/`의 코드와 경로는 유지하고 원본의 매핑 실행 루트를 `mapping/`에 추가했습니다. 원본 라이선스·출처는 [third_party/README.md](third_party/README.md)에 보존했습니다. 소스별 정확한 해시는 [UPSTREAM_IMPORT.json](UPSTREAM_IMPORT.json)에 기록되어 있습니다. 원본 커밋 기록은 원본 저장소에서 확인할 수 있고, 개인 저장소에는 출처를 명시한 소스 스냅샷으로 가져왔습니다.

## 실행 위치

원본 문서의 저장소 루트는 이 저장소에서는 `mapping/`입니다. 원본에 남아 있는 개발자 PC의 절대 경로는 현재 작업 경로로 바꿔 사용하세요.

```bash
cd mapping
python3 -m pip install -r requirements.txt
# requirements.txt 주석과 각 모듈 문서에 명시된 PyQt5/OpenCV/pytest 등도 준비
python3 -m pytest tests/handheld_mapping/test_terrain.py -q
```

ORB-SLAM3, RealSense, Isaac Sim 및 실기 장비는 해당 문서에 따라 별도로 준비해야 합니다. 센서 융합·매핑·경로 계획 코드를 가져온 것이며, 기존 RL과 연결된 실기 임무의 성공률을 새로 측정한 것은 아닙니다.

## 선택 자산

방송 화면용 대형 mission/teleop 캐시와 일부 실험·문서 그림/지도는 소스와 분리했습니다. 파일별 고정 커밋 URL·크기·Git blob 해시는 [UPSTREAM_ASSETS.json](UPSTREAM_ASSETS.json)에 있습니다.

```bash
python3 download_upstream_assets.py --group assets --list
python3 download_upstream_assets.py --group assets
```

다운로더는 다른 내용의 기존 로컬 파일을 덮어쓰지 않고, 다운로드 후 해시와 크기를 검사합니다.

## 확인 범위

가져온 Python 소스의 문법 검사 통과. 기존 NumPy 정책·추정기 로그 테스트 3개를 직접 실행해 통과했습니다. ROS·MuJoCo·GPU·실제 센서가 필요한 전체 테스트는 수행하지 않았습니다.
