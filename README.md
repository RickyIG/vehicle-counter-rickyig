<a name="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/RickyIG/vehicle-counter-rickyig">
    <img src="https://upload.wikimedia.org/wikipedia/en/f/fe/Autowerks_European.jpg" alt="Logo" width="150" height="150">
  </a>

<h3 align="center">Vehicle Counter RickyIG</h3>

  <p align="center">
    Real-time vehicle counting system using OpenVINO and MediaMTX - optimized for CPU performance, infinite video looping, embedded metadata on frames, and RTSP/HTTP stream output via Docker.
    <br />
    <a href="https://github.com/RickyIG/Vehicle-counter-rickyig"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/RickyIG/Vehicle-counter-rickyig">View Demo</a>
    ·
    <a href="https://github.com/RickyIG/Vehicle-counter-rickyig/issues">Report Bug</a>
    ·
    <a href="https://github.com/RickyIG/Vehicle-counter-rickyig/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Atlanta_75.85.jpg/1280px-Atlanta_75.85.jpg" alt="Wallpaper">

The Vehicle Counter project is a real-time video analytics service designed to detect and count vehicles efficiently using Intel's OpenVINO toolkit. Leveraging OpenVINO's optimization capabilities, the system performs high-speed inference on CPU-based machines, enabling deployment on edge devices without requiring expensive GPUs.

The service processes video input in an infinite loop to provide continuous monitoring and streams the processed video with embedded metadata (such as vehicle counts and speeds) through MediaMTX — a robust RTSP/HTTP streaming server. This design allows easy access to the live counting stream via web browsers or any RTSP-compatible client.

The entire solution is packaged using Docker for consistent and straightforward deployment across various environments. The project emphasizes simplicity by embedding metadata directly into the video frames, avoiding the need for external databases or complex data storage solutions.

This system is ideal for traffic monitoring, smart city applications, and infrastructure planning where real-time vehicle counting and lightweight deployment are essential.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Built With

[![Python][Python]][Python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
- Docker (version 20.10 or newer recommended) <br/>
Install from: https://docs.docker.com/get-docker/
- Docker Compose (if using docker-compose to run the services)<br/>
Install from: https://docs.docker.com/compose/install/
- Internet connection to pull required Docker images.

### Installation

1. Install Docker & Docker Compose<br/>
   Make sure Docker and Docker Compose are installed on your system.

2. Pull Docker Images <br/>
   Pull the Vehicle Counter and MediaMTX (streaming server) images:
   ```sh
   docker pull rickyindrag/vehicle-counter-cpu-rickyig:latest
   docker pull bluenviron/mediamtx:latest
   ```


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

This is an example of how to list things you need to run the software.

1. Run the Vehicle Counter Service via Docker Compose <br/>
   This is the recommended way to run the service.
   - Clone the repository and pull the image:
     ```sh
     git clone https://github.com/your-username/vehicle-counter.git
     cd vehicle-counter
     docker-compose pull
     ```
   - Start the service:
     ```sh
     docker-compose up -d
     ```
   - Stop the service:
     ```sh
     docker-compose down
     ```
   - To override the model or RTSP URL: <br/>
     Edit the docker-compose.yml file:
     ```sh
     command: python vehicle_counter.py --model=models/yolo11n_int8_openvino_model --rtsp_url=rtsp://host.docker.internal:8554/mystream
     ```

2. Run the Vehicle Counter Service via Docker Run (Alternative) <br/>
   Note: MediaMTX must be running before starting this container. <br/>
   Before running the Vehicle Counter service, make sure MediaMTX is up and running:
   ```sh
   docker run --rm -it \
   -p 8554:8554 -p 1935:1935 -p 8888:8888 -p 8889:8889 \
   bluenviron/mediamtx
   ```
   This starts MediaMTX and exposes:
   - rtsp://localhost:8554 (RTSP stream)
   - http://localhost:8888 (MediaMTX web interface)

   Linux
   ```sh
   docker run --rm \
   --add-host=host.docker.internal:host-gateway \
   rickyindrag/vehicle-counter-cpu-rickyig:latest \
   python vehicle_counter.py --rtsp_url=rtsp://host.docker.internal:8554/mystream
   ```

   Windows / macOS:
   ```sh
   docker run --rm \
   rickyindrag/vehicle-counter-cpu-rickyig:latest \
   python vehicle_counter.py --rtsp_url=rtsp://host.docker.internal:8554/mystream
   ```

   Custom model example (Linux):
   ```sh
   docker run --rm \
   --add-host=host.docker.internal:host-gateway \
   rickyindrag/vehicle-counter-cpu-rickyig:latest \
   python vehicle_counter.py \
   --model=models/yolo11n_openvino_model \
   --rtsp_url=rtsp://host.docker.internal:8554/mystream
   ```

   

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap & Goals
This project was developed to fulfill the following technical goals:

- [x] Run vehicle counting using OpenVINO for fast and efficient inference on CPU-based systems.

- [x] Stream output via MediaMTX, enabling access over RTSP and HTTP.

- [x] Implement infinite video looping for continuous vehicle counting without service interruption.

- [x] Package the entire service using Docker for easy deployment and reproducibility.

- [x] Create a complete GitHub repository with full documentation for the implementation and setup.

- [x] Record a demo video showcasing the successful execution of the service.

Success Criteria
- [x] The output stream is accessible via browser through MediaMTX (HTTP/RTSP).

- [x] The vehicle counting metadata is embedded directly into the video frames — no separate storage or database is required.


See the [open issues](https://github.com/RickyIG/Vehicle-counter-rickyig/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Ricky Indra Gunawan - rickyindra53@gmail.com

Project Link: [https://github.com/RickyIG/vehicle-counter-rickyig](https://github.com/RickyIG/vehicle-counter-rickyig)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
<!-- ## Acknowledgments -->

<!-- * []() -->
<!-- * []() -->
<!-- * []() -->

<!-- <p align="right">(<a href="#readme-top">back to top</a>)</p> -->



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/RickyIG/Vehicle-counter-rickyig.svg?style=for-the-badge
[contributors-url]: https://github.com/RickyIG/Vehicle-counter-rickyig/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/RickyIG/Vehicle-counter-rickyig.svg?style=for-the-badge
[forks-url]: https://github.com/RickyIG/Vehicle-counter-rickyig/network/members
[stars-shield]: https://img.shields.io/github/stars/RickyIG/Vehicle-counter-rickyig.svg?style=for-the-badge
[stars-url]: https://github.com/RickyIG/Vehicle-counter-rickyig/stargazers
[issues-shield]: https://img.shields.io/github/issues/RickyIG/Vehicle-counter-rickyig.svg?style=for-the-badge
[issues-url]: https://github.com/RickyIG/Vehicle-counter-rickyig/issues
[license-shield]: https://img.shields.io/github/license/RickyIG/Vehicle-counter-rickyig.svg?style=for-the-badge
[license-url]: https://github.com/RickyIG/Vehicle-counter-rickyig/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/rickyindrag
[product-screenshot]: images/screenshot.png
[Python]: https://www.python.org/static/community_logos/python-logo.png
[Python-url]: https://python.org/
