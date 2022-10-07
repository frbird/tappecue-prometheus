<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- [![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url] -->
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![GNU License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/apleto/tappecue-prometheus">
    <img src="images/apleto-logo-header.png" alt="Logo" width="300" height="63">
  </a>

<h3 align="center">Tappecue to Prometheus</h3>

  <p align="center">
    Get your grill temperatures into Prometheus and Grafana!
    <br />
    <!-- <a href="https://github.com/apleto/tappecue-prometheus"><strong>Explore the docs »</strong></a> -->
    <!-- <br /> -->
    <br />
    <!-- <a href="https://github.com/apleto/tappecue-prometheus">View Demo</a>
    · -->
    <a href="https://github.com/apleto/tappecue-prometheus/issues">Report Bug</a>
    ·
    <a href="https://github.com/apleto/tappecue-prometheus/issues">Request Feature</a>
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

<br></br>
[![Product Name Screen Shot][product-screenshot]](https://example.com)

<br></br>
<!-- ABOUT THE PROJECT -->
## About The Project

<!-- Here's a blank template to get started: To avoid retyping too much info. Do a search and replace with your text editor for the following: `apleto`, `repo_name`, `twitter_handle`, `linkedin_username`, `email_client`, `email`, `project_title`, `project_description` -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python3]][Python-url]
<!-- * [![Next][Next.js]][Next-url]
* [![React][React.js]][React-url]
* [![Vue][Vue.js]][Vue-url]
* [![Angular][Angular.io]][Angular-url]
* [![Svelte][Svelte.dev]][Svelte-url]
* [![Laravel][Laravel.com]][Laravel-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![JQuery][JQuery.com]][JQuery-url] -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

First, be sure you have everything setup in the config.yaml file. This loads your Tappecue account info so that the script can query the API, and it also allows you to tweak a few configuration settings such as:

* check_probe_delay - This is how often the script queries for temperature probe data. (seconds)
* no_session_delay - This sets how long to wait before checking for an active session if one was not already found. (seconds)

This is built to use a single TCP session when an active session is found so there shouldn't be too much load when checking for probe data oftern.

You could simply run the file "tappecue-monitor.py" on your local machine but the better way is to run it as a docker container. I don't have this on a public repo yet so you'll have to build the container yourself until then.

If you do decide to just run the script without a container be sure to install the Python requirements.

```sh
pip install -r requirements.txt
```

### Prerequisites

This only works with Tappecue thermometers. You can go check out there products here: [Tappecue](https://www.tappecue.com/)

<!-- 
### Installation

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/apleto/tappecue-prometheus.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'ENTER YOUR API';
   ``` -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

### Using Docker (preferred)
Docker Compose makes it really straightforward. From the directory containing the docker-compose file run:
```sh
docker-compose up -d
```
That's it!!! The container will mount the config.yaml file and start polling the Tappecue API for an active session. When a session is found it will start checking for probe data. This data is exposed as prometheus metrics on the port you mapped in the docker-compose.yaml file. 

If you going to run the script directly you'll need to do the following:
* Install the Python requirements
   ```sh
   pip install -r requirements.txt
   ```
* Make sure the config file is in the same directory as tappecue-monitor.py
* Run tappecue-monitor.py
   ```sh
   python tappecue-monitor.py
   ```

To get the data into Grafana you'll need to configure a Prometheus job to scrape the data or run the Grafana Agent to scrape the data.

<!-- _For more examples, please refer to the [Documentation](https://example.com)_ -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
<!-- ## Roadmap

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3
    - [ ] Nested Feature -->

See the [open issues](https://github.com/apleto/tappecue-prometheus/issues) for a full list of proposed features (and known issues). 

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

<!-- Your Name - [@twitter_handle](https://twitter.com/twitter_handle) - email@email_client.com -->

Project Link: [https://github.com/apleto/tappecue-prometheus](https://github.com/apleto/tappecue-prometheus)

Check out our other cool projects here [https://github.com/apleto](https://github.com/apleto)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* This uses the API that [frankdice](https://github.com/frankdice/tappecue-api) put together.  Thanks frankdice!
<!-- * []()
* []() -->

<p align="right">(<a href="#readme-top">back to top</a>)</p>

[![buymeacoffee][buymeacoffee-shield]][buymeacoffee-url]


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
[buymeacoffee-url]: https://www.buymeacoffee.com/castletx4
[contributors-shield]: https://img.shields.io/github/contributors/apleto/tappecue-prometheus.svg?style=for-the-badge
[contributors-url]: https://github.com/apleto/tappecue-prometheus/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/apleto/tappecue-prometheus.svg?style=for-the-badge
[forks-url]: https://github.com/apleto/tappecue-prometheus/network/members
[stars-shield]: https://img.shields.io/github/stars/apleto/tappecue-prometheus.svg?style=for-the-badge
[stars-url]: https://github.com/apleto/tappecue-prometheus/stargazers
[issues-shield]: https://img.shields.io/github/issues/apleto/tappecue-prometheus.svg?style=for-the-badge
[issues-url]: https://github.com/apleto/tappecue-prometheus/issues
[license-shield]: https://img.shields.io/github/license/apleto/tappecue-prometheus.svg?style=for-the-badge
[license-url]: https://github.com/github/license/apleto/tappecue-prometheus/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/matt-castle-5b04683/
[product-screenshot]: images/screenshot2.png
[Python3]: https://img.shields.io/pypi/pyversions/prometheus-client
[Python-url]: https://www.python.org/
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 