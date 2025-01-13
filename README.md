# Redis Cloud Platform

이 프로젝트는 Redis 인스턴스를 관리하는 시스템으로, Redis 인스턴스의 생성, 삭제, 시작, 중지 및 파일 시스템과의 동기화를 지원합니다. 

Python과 서브프로세스 관리, Redis 클라이언트 라이브러리를 사용하여 Redis 인스턴스를 관리하고 지정된 디렉토리 구조 내에서 효율적으로 운영되도록 합니다.

## 주요 기능  

Redis 인스턴스 생성: 고유한 구성 파일과 랜덤 비밀번호를 사용하여 Redis 인스턴스를 생성합니다

Redis 인스턴스 시작/중지: Redis 인스턴스를 필요에 따라 시작하고 중지할 수 있습니다. 프로세스 관리 기능을 통해 서비스 상태를 제어하게 됩니다.

## 오류 처리 

FileNotFoundError: 구성 파일이 없을 경우

RuntimeError: 프로세스 관리 실패 시

ValueError: 저장소에서 Redis 인스턴스를 찾을 수 없을 경우

## 준비  

서버 시작 전 서비스 디렉토리와 redis-server 프로그램의 경로를 설정해야 합니다
