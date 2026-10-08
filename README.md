<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/yoshiko-tsuka/User-Match-Engine-Visualizer">
    <img src="https://raw.githubusercontent.com/yoshiko-tsuka/User-Match-Engine-Visualizer/main/images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">User-Match-Engine-Visualizer</h3>

  <p align="center">
    A 2-stage user compatibility gating & multi-channel similarity ranking visualization engine built with FastAPI.
    <br />
    <a href="https://github.com/yoshiko-tsuka/User-Match-Engine-Visualizer"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://user-match-engine-visualizer.onrender.com/">View Demo</a>
    &middot;
    <a href="https://github.com/yoshiko-tsuka/User-Match-Engine-Visualizer/issues">Report Bug</a>
    &middot;
    <a href="https://github.com/yoshiko-tsuka/User-Match-Engine-Visualizer/issues">Request Feature</a>
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
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

**User-Match-Engine-Visualizer** is an interactive visualization tool and REST API designed to demonstrate a **two-stage recommendation and matching architecture**:

1. **Stage 1: Hard Compatibility Gate**
   - Evaluates bidirectional hard constraints such as geospatial distance bounds (computed via Haversine metric) and age preference boundaries.
   - Instantly filters out non-matching user candidate pairs before expensive score computations.
2. **Stage 2: Multi-Channel Ranking Layer**
   - **Professional Channel**: High-dimensional vector embedding comparison using **Cosine Similarity**.
   - **Interests Channel**: Categorical interest overlap evaluated using **Jaccard Similarity**.
   - Aggregates multi-channel scores using customizable normalized weighting.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python-shield]][Python-url]
* [![FastAPI][FastAPI-shield]][FastAPI-url]
* [![Docker][Docker-shield]][Docker-url]
* [![Jinja2][Jinja2-shield]][Jinja2-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Follow these steps to set up and run the matching engine visualizer locally.

### Prerequisites

* **Python 3.10+** or **Docker**
* **pip** (Python package manager)

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yoshiko-tsuka/User-Match-Engine-Visualizer.git
   ```
2. Navigate to the project directory:
   ```sh
   cd User-Match-Engine-Visualizer
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Start the FastAPI application:
   ```sh
   uvicorn main:app --reload
   ```
5. Open your browser and navigate to `http://127.0.0.1:8000`.

#### Running with Docker
```sh
docker-compose up --build
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

### Web Interface
Access `http://127.0.0.1:8000/` or the live demo at [user-match-engine-visualizer.onrender.com](https://user-match-engine-visualizer.onrender.com/) to interactively select source and target users, view gating pass/fail reasons, and inspect channel breakdown scores.

### API Endpoint
Calculate match compatibility and score programmatically:

```http
GET /api/v1/match?source_user_id=user_001&target_user_ids=user_002&target_user_ids=user_003
```

#### Response Example
```json
{
  "source_user_id": "user_001",
  "matches": [
    {
      "target_user_id": "user_002",
      "is_compatible": true,
      "compatibility_reason": "Passed all core compatibility metrics.",
      "final_rank_score": 0.7303,
      "channel_breakdown": {
        "professional_similarity": 0.7954,
        "interests_overlap": 0.6
      }
    }
  ],
  "response_time_ms": 0.14
}
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [x] Two-stage filtering & ranking implementation
- [x] Web visualization interface with Jinja2 templates
- [x] Docker containerization & cloud deployment on Render
- [ ] Async database I/O and Graph DB integration
- [ ] Batch query optimization for N+1 query avoidance

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Yoshiko Tsuka - [GitHub](https://github.com/yoshiko-tsuka) - [LinkedIn](https://www.linkedin.com/in/yoshikotsuka/)

Project Link: [https://github.com/yoshiko-tsuka/User-Match-Engine-Visualizer](https://github.com/yoshiko-tsuka/User-Match-Engine-Visualizer)

Live Demo: [https://user-match-engine-visualizer.onrender.com/](https://user-match-engine-visualizer.onrender.com/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/yoshiko-tsuka/User-Match-Engine-Visualizer.svg?style=for-the-badge
[contributors-url]: https://github.com/yoshiko-tsuka/User-Match-Engine-Visualizer/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/yoshiko-tsuka/User-Match-Engine-Visualizer.svg?style=for-the-badge
[forks-url]: https://github.com/yoshiko-tsuka/User-Match-Engine-Visualizer/network/members
[stars-shield]: https://img.shields.io/github/stars/yoshiko-tsuka/User-Match-Engine-Visualizer.svg?style=for-the-badge
[stars-url]: https://github.com/yoshiko-tsuka/User-Match-Engine-Visualizer/stargazers
[issues-shield]: https://img.shields.io/github/issues/yoshiko-tsuka/User-Match-Engine-Visualizer.svg?style=for-the-badge
[issues-url]: https://github.com/yoshiko-tsuka/User-Match-Engine-Visualizer/issues
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/yoshikotsuka/
[Python-shield]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[FastAPI-shield]: https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white
[FastAPI-url]: https://fastapi.tiangolo.com/
[Docker-shield]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
[Jinja2-shield]: https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge&logo=jinja&logoColor=white
[Jinja2-url]: https://jinja.palletsprojects.com/

