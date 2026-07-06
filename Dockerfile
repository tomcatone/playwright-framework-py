# 视觉回归测试的基准图和比对必须在同一浏览器版本+同一操作系统环境下进行，
# 否则字体渲染、抗锯齿差异会导致大量误报。这里直接用官方 Playwright 镜像，
# 版本号要和 requirements.txt 里的 playwright==1.48.0 保持一致。
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 本地生成/更新视觉回归基准图时，用这个镜像跑，保证和CI环境完全一致：
#   docker build -t pw-tests .
#   docker run --rm -v $(pwd)/tests:/app/tests pw-tests pytest --update-snapshots
CMD ["pytest"]
