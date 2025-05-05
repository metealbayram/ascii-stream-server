# ascii-stream-server
# ASCII Art Video Streaming Server (`sserver`)

This project is a **multi-threaded ASCII art video streaming server** built with **Python**, designed to simulate video playback using ASCII characters via TCP sockets. It demonstrates key Operating Systems concepts such as **threads**, **semaphores (locks)**, and **socket communication**.

## 🧠 Project Purpose

This application was developed as part of an Operating Systems experiment to gain hands-on experience with:

- Multi-threaded programming
- Critical section management using locks
- Concurrent client handling
- TCP socket communication
- File reading and real-time broadcasting

## 🚀 Features

- Supports **3 separate channels** (like TV channels)
- Each channel reads frames from a text file (e.g., `1.txt`, `2.txt`, `4.txt`)
- Clients can connect and **choose a channel** to view the stream
- Multiple clients can connect to the **same or different channels**
- Smooth ASCII "video" stream using line-by-line text updates

## 🖥️ Technologies Used

- **Python 3**
- **Threading**
- **Sockets**
- **Locks for synchronization**

## 📁 File Structure
├── server.py 
├── client.py 
├── 1.txt # Frame data for Channel 1
├── 2.txt # Frame data for Channel 2
├── 4.txt # Frame data for Channel 3
