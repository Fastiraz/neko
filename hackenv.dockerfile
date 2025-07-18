FROM kalilinux/kali-rolling:latest

ENV DEBIAN_FRONTEND=noninteractive

ENV DISPLAY=$DISPLAY

RUN apt-get update \
  && apt-get full-upgrade -y \
  && apt-get install -y --no-install-recommends \
  kali-linux-headless \
  wireshark \
  # kali-linux-everything \
  build-essential \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

CMD ["tail", "-f", "/dev/null"]
