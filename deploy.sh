#!/usr/bin/env bash
# 一键部署脚本：用于在Ubuntu服务器上安装依赖并启动量化交易系统。
set -euo pipefail

PROJECT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
VENV_DIR="$PROJECT_DIR/.venv"

function log_info() {
  echo "[INFO] $1"
}

log_info "更新系统包索引..."
sudo apt-get update

log_info "安装Python3及基础依赖..."
sudo apt-get install -y python3 python3-venv python3-pip

if [ ! -d "$VENV_DIR" ]; then
  log_info "创建Python虚拟环境..."
  python3 -m venv "$VENV_DIR"
fi

log_info "激活虚拟环境并安装项目依赖..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
  pip install -r "$PROJECT_DIR/requirements.txt"
else
  pip install backtrader yfinance apscheduler pandas
fi

log_info "初始化数据库..."
python3 -c "from database import init_db; init_db()"

log_info "部署完成，可使用如下命令运行系统："
cat <<USAGE
----------------------------------------
回测模式:   $VENV_DIR/bin/python main.py backtest
实盘调度:   $VENV_DIR/bin/python main.py
----------------------------------------
USAGE
