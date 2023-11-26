"""
This is where the implementation of the plugin code goes.
The myPlugin-class is imported from both run_plugin.py and run_debug.py
"""
import sys
import logging
from webgme_bindings import PluginBase

# Setup a logger
logger = logging.getLogger('myPlugin')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)  # By default it logs to stderr..
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class myPlugin(PluginBase):
  def main(self):
    active_node = self.active_node
    core = self.core
    self.namespace = None
    META = self.META
    # Log attributes of the active node
    self.log_node_attributes(active_node)
    # Process nodes to create game states
    all_states = self.process_nodes(active_node)

  def log_node_attributes(self, node):
    # Acquire the logger object
    logger = self.logger
    # Log various attributes of the node at different log levels
    logger.debug('path: {0}'.format(self.core.get_path(node)))
    logger.info('name: {0}'.format(self.core.get_attribute(node, 'name')))
    logger.warn('pos : {0}'.format(self.core.get_registry(node, 'position')))
    logger.error('guid: {0}'.format(self.core.get_guid(node)))

  def process_nodes(self, active_node):
    # Load the subtree of nodes starting from the active node
    nodesList = self.core.load_sub_tree(active_node)
    # Dictionary to map node paths to node objects
    self.nodes = {}
    # Iterate through each node in the subtree
    for node in nodesList:
      # Map node path to node object
      self.nodes[self.core.get_path(node)] = node
    # List to hold all game state dictionaries
    all_states = []
    for path in self.nodes:
      node = self.nodes[path]
      # If the node is a GameState instance, process it
      if self.core.is_instance_of(node, self.META['GameState']):
        # Create and store the game state dictionary
        game_state = self.create_game_state(node, self.nodes)
        all_states.append(game_state)
        # Log the game state dictionary
        self.logger.info(game_state)
    return all_states

  def create_game_state(self, node, nodesList):
    # Create a dictionary for the game state starting with the name
    game_state = {'name': self.core.get_attribute(node, 'name')} 
    # Get the path to the current player and store it in the game state
    current_player_path = self.core.get_pointer_path(node, 'currentPlayer')
    # Load all children of the GameState node
    children = self.core.load_children(node)
    game_state['currentPlayer'] = self.core.get_attribute(
      nodesList[self.core.get_pointer_path(node, "currentPlayer")], 
      'name')
    # Store the current move details in the game state
    current_move_piece = self.nodes[self.core.get_pointer_path(node,"currentMove")]
    current_move_tile = self.core.get_parent(current_move_piece)
    current_move_color = self.core.get_attribute(current_move_piece, "color")
    current_move_tile_row = self.core.get_attribute(current_move_tile, "row")
    current_move_tile_column = self.core.get_attribute(current_move_tile, "column")
    # Add the current move details to the game state
    game_state['currentMove'] = {
      'color': current_move_color,
      'row': int(current_move_tile_row),
      'column': int(current_move_tile_column)
    }
    # Process and store the game board in the game state
    for child in children:
      if self.core.is_instance_of(child, self.META['Board']):
        game_state['board'] = self.initialize_board(child)
    return game_state

  def initialize_board(self, board_node):
    # Initialize a list to represent the board
    board = [['' for _ in range(8)] for _ in range(8)]
    # Load all child nodes of the board, which should be tiles
    tiles = self.core.load_children(board_node)
    # Process each tile for flipping pieces
    for tile in tiles:
      if self.core.is_instance_of(tile, self.META["Tile"]):
        flips = []
        row = self.core.get_attribute(tile, "row")
        column = self.core.get_attribute(tile, "column")
        pieces = self.core.load_children(tile)
        # Initialize color as None in case there is no piece on the tile
        color = None
        if pieces:
          piece = pieces[0]
          if self.core.is_instance_of(piece, self.META['Piece']):
            color = self.core.get_attribute(piece, 'color')
        for board_child in tiles:
          if self.core.is_instance_of(board_child, self.META["mightFlip"]):
            srcTile = self.core.get_parent(self.nodes[self.core.get_pointer_path(board_child,"src")])
            dstTile = self.core.get_parent(self.nodes[self.core.get_pointer_path(board_child,"dst")])
            if srcTile == tile:
               flips.append({
                 "column" : self.core.get_attribute(dstTile,"column"),
                 "row" : self.core.get_attribute(dstTile,"row")
               }) 
        board[column][row] = {"color": color, "flips": flips}
    return board

