![banner](saltatio_mortis/static/img/CopertinaRPG.jpg)

<p align='center'>
	<img alt="Static Badge" src="https://img.shields.io/badge/Version-1.0-blue?style=flat">
    <img alt="Last Commit" src="https://img.shields.io/github/last-commit/delectablerec/Gdr-flask?style=flat">
</p>

## Table of Contents

- [What is Saltatio Mortis?](#what-is-saltatio-mortis)
- [Why did we create it?](#why-did-we-create-it)
- [Features](#features)
- [Known Bugs](#known-bugs)
- [Future Updates](#future-updates)
- [Changelog](#changelog)
- [How to Contribute](#how-to-contribute)
- [Team](#team)
- [License](#license)

## What is Saltatio Mortis?
**Saltatio Mortis** is a web-based turn-based role-playing game of the _text-based_ type, where the player interacts with non-player characters *(NPCs)*, completes missions, and uses strategic items to progress in the game. The system features advanced management of characters, items, missions, and NPC behavioral strategies.

## Why did we create it?
The project was born for educational purposes as a group work, but the choice of the role-playing game proved to be ideal because it requires building a simulated world, with rules and custom behaviors, almost like a coded transposition of reality.

We found all of this to be an excellent exercise that allowed us first and foremost to develop **logical abilities**, **abstraction** and **collaboration** skills, to mature an approach to constant problem-solving using the Object-Oriented Programming *(OOP)* paradigm.

## Features
- Dynamic management of `characters` with attributes like health, attack, and dexterity.
- `Items` with extensible behaviors via derived classes.
- Structured `missions` with `environments`, enemies, and rewards.
- Configurable NPC behavioral `strategies` to define aggressive, defensive, or balanced gameplay styles.
- Data serialization and deserialization through *Marshmallow* for easy saving and loading.

## Known Bugs

## Future Updates
- Ability to create missions
- Ability to autonomously manage turns and attacks thanks to an additional *"Manual"* combat mode
- Ability to heal your characters once the battle is finished
- Addition of character equipment elements (armor, weapons)
- Credit recovery system based on obtained score (+ bonus in case of victory)
- Multiplayer mode
- 2D graphics engine

## Changelog
For the complete and detailed list of updates: [CHANGELOG.md](./CHANGELOG.md)

## How to Contribute
Your contribution is important! Feel free to help our project grow with a pull request featuring new functionalities, bug fixes, or improvements.

If you want to support development and future implementations, show us your support through the buttons below

[![Star](https://img.shields.io/github/stars/delectablerec/Gdr-flask?style=flat&cacheSeconds=10)](https://github.com/delectablerec/Gdr-flask/stargazers)
[![Fork](https://img.shields.io/github/forks/delectablerec/Gdr-flask?style=flat&cacheSeconds=10)](https://github.com/delectablerec/Gdr-flask/network/members)
[![Watch](https://img.shields.io/github/watchers/delectablerec/Gdr-flask?style=flat&cacheSeconds=10)](https://github.com/delectablerec/Gdr-flask/watchers)

Or follow [the project creator](https://github.com/delectablerec)

[![Followers](https://img.shields.io/github/followers/delectablerec?style=flat&cacheSeconds=10)](https://github.com/delectablerec)

## Team
- Ariotti Matteo
- Chiara Konrad
- Maddaloni Enrico
- Puccini Nicolò
- Fabrice Ghislain Tebou
- Trotti Enrico
- Yildiz Sidar

## License

This project is distributed under the MIT license.
See the LICENSE file for details.

## Topics for Oral Examination:

- ### Organizational methodology, task division and versioning (Enrico T.)

- ### Project structure in classes, blueprint (Matteo)

- ### Documentation standards, Docstring and Sphinx (Konrad)

- ### SQLAlchemy ORM, users, admin and privileges

- ### General software functioning and history (development chronology) (Nik)

- ### Transition to Flask, from console to web application (Enrico M.)

- ### Raspberry (Sidar)