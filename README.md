# Burglar

![Burglar](images/logo.png)

Burglar is an innovative game in the 'match 3' style that will twist your head off.

## Getting a Package to Play

Prebuilt packages of Burglar are available at [Itch.io](https://bueybr.itch.io/burglar) for download. Versions for Linux (32 bits) and Windows 10 (64 bits).

## Getting Started

To contribute in the development, you just need to clone the repository with:
```
$ git clone https://github.com/AlexPHorta/Burglar.git
```
Create a virtualenv with at least Python 3.7:
```
$ virtualenv -p3.7 burglar
```
Activate the virtual env:
```
$ source burglar/bin/activate
```
Install the dependencies:
```
$ pip install -r requirements.txt
```
### Prerequisites

Burglar depends on the following software to work:

* Python 3.7
* PyGame 1.9.6
* Pyinstaller 3.6 (just to create the packages)

## Running the tests

You can run the tests with ...

## Deployment

Burglar is available in standalone packages, built with Pyinstaller. The [burglar.spec](burglar.spec) file has been tested in Linux Mint 19.3 and Windows 10.

The package can be generated with:
```
$ pyinstaller burglar.spec
```
If you have another system you want available, edit the [burglar.spec](burglar.spec) file accordingly, generate and test the package. In case everything works fine, open a PR.

## Built With

### Sound effects
* [https://freesound.org/people/DrMinky/sounds/167045/](https://freesound.org/people/DrMinky/sounds/167045/) - [CC 3.0](https://creativecommons.org/licenses/by/3.0/)
* [https://freesound.org/people/kwahmah_02/sounds/256116/](https://freesound.org/people/kwahmah_02/sounds/256116/) - [CC 3.0](https://creativecommons.org/publicdomain/zero/1.0/)
* [https://freesound.org/people/7778/sounds/202312/](https://freesound.org/people/7778/sounds/202312/) - [CC 3.0](https://creativecommons.org/publicdomain/zero/1.0/)
* [https://freesound.org/people/ShadyDave/sounds/270657/](https://freesound.org/people/ShadyDave/sounds/270657/) - [CC 3.0](https://creativecommons.org/licenses/by/3.0/)
* [Copyright © 2011 Varazuvi™ (www.varazuvi.com)](https://freesound.org/people/Soughtaftersounds/sounds/145438/) - [CC 3.0](https://creativecommons.org/licenses/by/3.0/)

### Music
* *Marcato loop* by Shady Dave found on (https://www.freesound.org/people/ShadyDave/)

### Hacks
* Image with per pixel transparency blitted on lowered transparency surface: https://nerdparadise.com/programming/pygameblitopacity

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/Burglar/tags).

## Authors

* **Alexandre Paloschi Horta - Buey.net.br** - *Initial work* - [AlexPHorta](https://github.com/AlexPHorta)

### Concept
* **Alexandre Paloschi Horta** - (https://www.buey.net.br)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Guido, and the guys from Pygame;
* My wife, Thays, and my daughters, Bárbara and Lavínia.
