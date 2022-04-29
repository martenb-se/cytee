import React, {useState} from 'react';
import ArgumentTypeSelector from "../../../../shared/components/ArgumentTypeSelector";
import ArgumentDataFieldInput from "../../../../shared/components/ArgumentInputValueSelector";

const initState = {

}

function ObjectCreationTab({baseObject, onChangeCallback, label}) {

    const [objectState, setObjectState] = useState(initState);
    const [selectedObjectKey, setSelectedObjectKey] = useState('');
    const [keyLabel, setKeyLabel] = useState('');
    const [type, setType] = useState('undefined');
    const [value, setValue] = useState(undefined);

    function onLabelChangeCallback(e) {
        setKeyLabel(e.target.value);
    }

    function onTypeChangeCallback(e) {
        setType(e.target.value);
        switch(e.target.value) {
            case 'undefined':
            case 'null':
                setValue(undefined);
                break;
            case 'array':
                setValue([]);
                break;
            case 'boolean':
                setValue(false);
                break;
            case 'number':
                setValue(0);
                break;
            case 'string':
                setValue('');
                break;
            case 'object':
                setValue({});
                break;
        }
    }

    function onValueChangeCallback(e) {
        setValue(e.target.value)
    }

    function addCallback(e) {
        e.preventDefault();

        if (selectedObjectKey === '') {
            objectState[selectedObjectKey] = value;
        }

    }

    return (
        <div className ="create-object-tab-wrapper">
            <form
                onSubmit={addCallback}
            >
                <div className="mb-3">
                    <label className="form-label" htmlFor="create-object-select-object-key-input">Selected Key</label>
                    <select className="form-select" id="create-object-select-object-key-input">
                        <option >Choose...</option>
                        <option value="1">One</option>
                        <option value="2">Two</option>
                        <option value="3">Three</option>
                    </select>
                </div>
                <div className="input-group mb-3">
                    <span className="input-group-text">Key</span>
                    <input
                        type="text"
                        className="form-control"
                        placeholder="key"
                        value={keyLabel}
                        onChange={onLabelChangeCallback}
                    />
                </div>
                <div className="input-group mb-3">
                    <span className="input-group-text">Type</span>
                    <ArgumentTypeSelector
                        id="create-object-type-selector-input"
                        type={type}
                        onChangeCallback={onTypeChangeCallback}
                    />
                </div>
                <div className="input-group mb-3">
                    <span className="input-group-text">Value</span>
                    <ArgumentDataFieldInput
                        type={type}
                        value={value}
                        onChangeCallback={onValueChangeCallback}
                        />
                </div>
                <button type="submit" className="btn btn-primary">Add</button>
            </form>
            <div className="creat-object-object-viewer">
                <div>
                    <pre>{JSON.stringify(objectState)}</pre>
                </div>
            </div>
        </div>
    );

}

function structToObject() {

}

function objectToStruct() {

}

/*
    function createObjectView(obj) {

        const keyList = Object.keys(obj);

        return keyList.map(key => {
            if (obj[key] === null){
                return <li>{key}: null</li>
            } else if (Array.isArray(obj[key])) {
                return <li>{key}: [Array]</li>
            }
            switch(typeof obj[key]) {
                case 'object':
                    return (
                        <details open>
                            <summary>{key}:{"{"}</summary>
                            <ul>
                                {createObjectView(obj[key])}
                            </ul>
                            {"}"}
                        </details>
                    );
                case 'boolean':
                case 'string':
                    return <li>{key}: {obj[key].toString()}</li>
                case 'undefined':
                    return <li>{key}: undefined</li>
                default:
                    return <li>{key}: [unable to detect type of value]</li>
            }
        });
    }

    return (
        <div>
            <div>
                <h1>
                    Object Creation Tab
                </h1>
                <div>
                    <span>Currently selected Object</span>
                    <div>{selectedObjectKey}</div>
                </div>

                <span>Label: </span>
                <input
                    type={'text'}
                    value={keyLabel}
                    onChange={onLabelChangeCallback}
                />
                <span>Type: </span>
                <ArgumentTypeSelector
                    type={type}
                    value={value}
                    onChangeCallback={onTypeChangeCallback}
                />
                <span>Value: </span>
                <ArgumentDataFieldInput
                    type={type}
                    value={value}
                    onChangeCallback={onValueChangeCallback}
                />
            </div>
            <div>
                {"{"}
                <details open>
                    <summary>root</summary>
                    <ul>
                        {createObjectView(baseObject)}
                    </ul>

                </details>
                {"}"}
            </div>
        </div>
    )
 */

export default ObjectCreationTab;
