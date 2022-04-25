import React from 'react';

function CustomTab(props) {

    return (
        <div className={'tab ' + props.tabName}>
            {props.children}
        </div>
    );
}

export default CustomTab;