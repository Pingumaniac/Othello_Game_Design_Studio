# Othello_Game_Design_Studio
CS 6388 Model-Integrated Computing final project.

## Introduction
Othello Game Studio is a comprehensive design studio for creating and playing the Othello (Reversi) game. This studio includes a visualizer, game logic plugins, and a meta-model for an immersive gaming experience.

## Installation Instructions

### Prerequisites
1. Node.js (version 20.9.0 LTS or higher)
2. Python3 (version 3.11.0 or higher, if applicable)

### Steps 
1. Open the terminal and clone the repository 
```
git clone https://github.com/Pingumaniac/Othello_Game_Design_Studio.git
cd [repository directory/myminiproject]
```
2. Install dependencies
```
npm install
npm install webgme
npm install webgme-bindings
pip3 install webgme-bindings
```
3. Download/Install Docker Desktop from the following url: https://www.docker.com/products/docker-desktop/
4. Download/Install the latest version of mongo in Docker Image.
5. Create an image of mongo. For optional settings, please set the Host path as
```
[repository directory]/DB
```
and set the Container path as
```
/data/db
```
6. From the terminal, enter the following command.
```
node app.js
```
7. Open your browser and navigate to [http://localhost:8888].

## Implementation Description

### Structure
* src/: Contains the source code for the studio.
* plugins/: Game logic plugins (Highlight valid tiles, Counting pieces, Flipping, Undo, Auto).
* visualizers/: Visualization components for the game.
* meta/: Meta-model for the game.

## Technologies Used
1. React.js for front-end visualization.
2. Node.js for back-end services.
3. WebGME for model integration.
4. Python for creating the plugins.


## Usage Description

### Playing the Game
1. Start a New Game:
* Click on 'New Game' to initialize a new Othello board.
2. Making Moves:
* Click on a valid tile to place your piece.
* The valid tiles are highlighted based on the current game state.
3. Game Progression:
* The game automatically counts and displays the number of pieces for each color.
* After each move, the board updates to reflect the new state.
4. Undo Functionality:
* Click 'Undo' to revert to the previous state.
5. Auto Play (Optional):
* Click 'Auto' to let the computer make a move.

### End of the Game
* The game concludes when no valid moves are available.
* The final score is displayed, indicating the winner.

## Repository Contents
* README.md: This documentation file.
* src/: Source code directory.

## Deployment
Follow the installation instructions to deploy the Othello Game Studio on your local machine. Ensure all dependencies are installed for a smooth setup.
