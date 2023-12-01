import { useState } from 'react';
import CONSTANTS from './constants';

export default function Tile({ position, piece, onMove }) {
    const [hasMouse, setMouse] = useState(false);

    const onTileClick = () => {
        if (piece === CONSTANTS.PIECE.EMPTY) {
            onMove(position);
        }
    };

    const onMouseEnter = () => {
        setMouse(true);
    };

    const onMouseLeave = () => {
        setMouse(false);
    };

    const getPiece = () => {
        const style = {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '100%',
            height: '100%',
            borderRadius: '50%',
            backgroundColor: piece === CONSTANTS.PIECE.BLACK ? 'black' : 'white',
        };

        if (piece !== CONSTANTS.PIECE.EMPTY) {
            return <div style={style}></div>;
        }
        return null;
    };

    const getTile = () => {
        const style = {
            width: '100px',
            height: '100px',
            borderColor: 'black',
            borderWidth: '1px',
            borderStyle: 'solid',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#1D7874',
            opacity: hasMouse && piece === CONSTANTS.PIECE.EMPTY ? 0.5 : 1,
        };

        return (
            <div onClick={onTileClick}
                style={style}
                onMouseEnter={onMouseEnter}
                onMouseLeave={onMouseLeave}>
                {getPiece()}
            </div>
        );
    };

    return getTile();
}
