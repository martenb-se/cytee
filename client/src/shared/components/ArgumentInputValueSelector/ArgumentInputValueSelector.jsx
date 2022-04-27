import React from 'react';
import {ObjectCreator} from "../../../Project/components/TestCreatorSection/ArgumentTab/ArgumentTab";

function ArgumentDataFieldInput({type, value, onChangeCallback}) {

    switch(type) {
        case 'undefined':
        case 'null':
            return <input
                type="text"
                disabled
                value={type}
            />
        case 'boolean':
            return (
                <select
                    className="form-select"
                    defaultValue={value}
                    onChange={onChangeCallback}
                >
                    <option value={false}>False</option>
                    <option value={true}>True</option>
                </select>
            )
        case 'number':
            return (
                <input
                    type ="number"
                    value={value}
                    onChange={onChangeCallback}
                />
            )
        case 'string':
            return <input
                type="text"
                onChange={onChangeCallback}
                value={value}
            />
        case 'object':
            /*return <ObjectCreator />*/
        default:
            return <div>[Input]</div>
    }
}

export default ArgumentDataFieldInput;