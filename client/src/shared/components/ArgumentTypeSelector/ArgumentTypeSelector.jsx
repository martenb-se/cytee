import React from "react";

function ArgumentTypeSelector({type, onChangeCallback}) {
    return (
        <select value={type} onChange={onChangeCallback}>
            <option value={'array'}>Array</option>
            <option value={'boolean'}>Boolean</option>
            <option value={'null'}>Null</option>
            <option value={'number'}>Number</option>
            <option value={'object'}>Object</option>
            <option value={'string'}>String</option>
            <option value={'undefined'}>Undefined</option>
        </select>
    )
}

export default ArgumentTypeSelector;