import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { icon } from '@fortawesome/fontawesome-svg-core/import.macro'
import { useState } from 'react';

export default function Tile({player, piece, position, win}) {

    const [hasMouse, setMouse, onHasMouseChange] = useState(false);

    const onTileClick = () => {
        if (piece === CONSTANTS.PIECE.EMPTY) {
            WEBGME_CONTROL.playerMoves(player, position);
        }
    }

    const onMouseEnter = () => {
        setMouse(true);
    }

    const onMouseLeave = () => {
        setMouse(false);
    }

    const getPiece = () => {
        return null;
    }

    const getTile = () => {
        const style = {
            width:'100px', 
            height:'100px', 
            borderColor:'black',
            borderWidth:'2px',
            border:'solid'};

            if (win && win.positions.indexOf(position) !== -1) {
                style.backgroundColor = '#EE2E31';
            } else if(hasMouse) {
                if(piece === CONSTANTS.PIECE.EMPTY) {
                    style.backgroundColor = '#F4C095';
                } else {
                    style.backgroundColor = '#1D7874';
                    style.opacity = 0.75;
                }
            }
            return (<div onClick={onTileClick} 
                style={style}
                onMouseEnter={onMouseEnter}
                onMouseLeave={onMouseLeave}>{getPiece()}</div>);
    }

    return getTile();
}