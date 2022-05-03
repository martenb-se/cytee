import React from 'react';
import {ObjectCreator} from "../../../Project/components/TestCreatorSection/ArgumentTab/ArgumentTab";

function ArgumentDataFieldInput(
    {
        argumentData,
        onChangeCallback,
        disabled,
        onEdit,
    }) {

    if (argumentData === undefined) {
        return <div>asdasd</div>
    }

    switch(argumentData.type) {
        case 'undefined':
        case 'null':
            return <input
                className="form-control"
                type="text"
                disabled
                value={argumentData.type}
            />
        case 'boolean':
            return (
                <select
                    className="form-select"
                    defaultValue={argumentData.value}
                    disabled={disabled}
                    onChange={onChangeCallback}
                >
                    <option value={false}>False</option>
                    <option value={true}>True</option>
                </select>
            )
        case 'number':
            return (
                <input
                    className="form-control"
                    type ="number"
                    value={argumentData.value}
                    disabled={disabled}
                    onChange={onChangeCallback}
                />
            )
        case 'string':
            return <input
                className="form-control"
                type="text"
                disabled={disabled}
                onChange={onChangeCallback}
                value={argumentData.value}
            />
        case 'object':
        case 'array':
            return (
                <button
                    className="btn btn-secondary"
                    onClick={e => {
                        e.preventDefault();
                        onEdit(argumentData);
                    }}
                    disabled={disabled}
                >
                    Edit
                </button>
            )
        default:
            return <div>[Input]</div>
    }
}



export default ArgumentDataFieldInput;