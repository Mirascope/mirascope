FROM docker.io/cloudflare/sandbox:0.7.0

# Install Node.js 22 (required by openclaw) and rclone (for R2 persistence)
# The base image has Node 20, we need to replace it with Node 22
ENV NODE_VERSION=22.13.1
RUN ARCH="$(dpkg --print-architecture)" \
    && case "${ARCH}" in \
         amd64) NODE_ARCH="x64" ;; \
         arm64) NODE_ARCH="arm64" ;; \
         *) echo "Unsupported architecture: ${ARCH}" >&2; exit 1 ;; \
       esac \
    && apt-get update && apt-get install -y xz-utils ca-certificates rclone unzip \
    && curl -fsSLk https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${NODE_ARCH}.tar.xz -o /tmp/node.tar.xz \
    && tar -xJf /tmp/node.tar.xz -C /usr/local --strip-components=1 \
    && rm /tmp/node.tar.xz \
    && node --version \
    && npm --version

# Install bun
RUN curl -fsSL https://bun.sh/install | bash \
    && ln -sf /root/.bun/bin/bun /usr/local/bin/bun \
    && bun --version
ENV PATH="/root/.bun/bin:$PATH"

# Install uv (Python package manager)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && ln -sf /root/.local/bin/uv /usr/local/bin/uv \
    && ln -sf /root/.local/bin/uvx /usr/local/bin/uvx \
    && uv --version

# Install Python 3.12 and mirascope with all extras
RUN uv python install 3.12 \
    && uv venv --python 3.12 /opt/mirascope-env \
    && uv pip install --python /opt/mirascope-env "mirascope[all]"
ENV PATH="/opt/mirascope-env/bin:$PATH"

# Install openclaw globally
RUN bun install -g openclaw \
    && openclaw --version

# Install mirascope TypeScript
RUN bun install -g mirascope

# Create openclaw and rclone config directories
RUN mkdir -p /root/.openclaw \
    && mkdir -p /root/.openclaw/workspace \
    && mkdir -p /root/.config/rclone

# Copy startup script
COPY start-openclaw.ts /usr/local/bin/start-openclaw.ts

# Set working directory
WORKDIR /root/.openclaw/workspace

# Expose the gateway port
EXPOSE 18789
