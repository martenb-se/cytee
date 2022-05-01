import React, {useState, useEffect} from 'react';
import ArgumentTypeSelector from "../../../../shared/components/ArgumentTypeSelector";
import ArgumentDataFieldInput from "../../../../shared/components/ArgumentInputValueSelector";
import './ObjectCreationTab.scss';

import cloneDeep from "lodash/cloneDeep";

// Creator Tab
function ObjectCreationTab({initBaseState, onChangeCallback, label}) {

    const [baseState, setBaseState] = useState(initBaseState);

    const [selectedScope, setSelectedScope] = useState('');
    const [selectedAttribute, setSelectedAttribute] = useState('');

    const [scopeList, setScopeList] = useState([]);
    const [attributeList, setAttributeList] = useState([]);

    const [attributeLabel, setAttributeLabel] = useState('');
    const [attributeType, setAttributeType] = useState('undefined');
    const [attributeValue, setAttributeValue] = useState(undefined);

    const [arrayIndex, setArrayIndex] = useState(0);

    const [errorMessage, setErrorMessage] = useState('');

    function getScope(base, scope, offset) {
        let stateRef = base, scopePath = undefined, i = 0;
        if (scope !== '') {
            scopePath = scope.match(/[^\[\].]+/g);
            while (i < scopePath.length + offset) {
                let currentAttribute = scopePath[i].match(/^\d+/g);
                if (currentAttribute !== null) {
                    stateRef = stateRef.value[currentAttribute];
                } else {
                    let index = stateRef.value.findIndex(argData => argData.argument === scopePath[i]);
                    stateRef = stateRef.value[index];
                }
                i++;
            }
        }

        return stateRef
    }

    function getAttribute(base, scope, attribute, offset) {
        const scopeRef = getScope(base, scope, offset);
        if (scopeRef.type === 'array')
            return scopeRef.value[arrayIndex];
        else
            return scopeRef.value.find(argData => argData.argument === attribute);
    }

    function getAttributeIndex(base, scope, attribute, offset) {
        const scopeRef = getScope(base, scope, offset);
        return scopeRef.value.findIndex(argData => argData.argument === attribute);
    }

    function deleteAttribute(base, scope, attribute, offset) {
        const stateRef = getScope(base, scope, offset);
        const attributeIndex = getAttributeIndex(base, scope, attribute, 0);
        stateRef.value.splice(attributeIndex, 1);
    }

    function checkValidLabel(label) {
        if (label === '') {
            setErrorMessage("Label can't be empty");
            return false;
        }

        const validLabel = label.match(/(^\d+|[^\w$]+)/g);
        if (validLabel !== null) {
            setErrorMessage('Label contains illegal characters');
            return false;
        }

        if (getAttributeIndex(baseState, selectedScope, label, 0) !== -1) {
            setErrorMessage(
                'Property with label \"' +
                label +
                "\" already exists in the scope \"" +
                ((selectedScope === '')?'root':selectedScope) +
                "\".");
            return false;
        }
        return true;
    }

    function generateBaseList(state, path) {
        const pathList = [];
        for (let i = 0; i < state.value.length; i++) {
            if ((state.value[i].type === 'object') || (state.value[i].type === 'array')) {
                let newPath;
                if (state.type === 'object') {
                    if (path === "") {
                        newPath = state.value[i].argument;
                    } else {
                        newPath = path + "." + state.value[i].argument;
                    }
                } else if (state.type === 'array') {
                    if (path === "") {
                        newPath = "[" + i + "]";
                    } else {
                        newPath = path + "[" + i + "]";
                    }
                }
                pathList.push(newPath);
                pathList.push(...generateBaseList(state.value[i], newPath));
            }
        }
        return pathList;
    }

    function generateAttributeList() {
        const attributeList = [];
        const stateRef = getScope(baseState, selectedScope, 0);
        for (let i = 0; i < stateRef.value.length; i++) {
            if (stateRef.type === 'array') {
                attributeList.push(i.toString());
            } else {
                attributeList.push(stateRef.value[i].argument);
            }
        }

        return attributeList;
    }

    function localChangeCallback() {
        onLocalChangeCallback({
            baseState: baseState,
            selectedScope: selectedScope,
            selectedAttribute: selectedAttribute,
            scopeList: scopeList,
            attributeList: attributeList,
            attributeLabel: attributeLabel,
            attributeType: attributeType,
            attributeValue: attributeValue,
            arrayIndex: arrayIndex,
            errorMessage: errorMessage,
        })
    }

    function onSelectedScopeChangeCallback(e) {
        setSelectedScope(e.target.value);
    }

    function onSelectedAttributeChangeCallback(e) {
        setSelectedAttribute(e.target.value);
    }

    function onAttributeLabelChangeCallback(e) {
        setAttributeLabel(e.target.value);
        setErrorMessage('');
    }

    function onAttributeTypeChangeCallback(e) {
        setAttributeType(e.target.value);
        switch(e.target.value) {
            case 'undefined':
            case 'null':
                setAttributeValue(undefined);
                break;
            case 'array':
                setAttributeValue([]);
                break;
            case 'boolean':
                setAttributeValue(false);
                break;
            case 'number':
                setAttributeValue(0);
                break;
            case 'string':
                setAttributeValue('');
                break;
            case 'object':
                setAttributeValue([]);
                break;
        }
    }

    function onAttributeValueChangeCallback(e) {
        setAttributeValue(e.target.value);
    }

    function selectedAttributeChange() {

        const stateRef = getScope(baseState, selectedScope, 0);
        if (stateRef.type === 'array') {
            if (selectedAttribute !== '') {
                setArrayIndex(parseInt(selectedAttribute));
                setAttributeType(stateRef.value[selectedAttribute.toString()].type);
                setAttributeValue(stateRef.value[selectedAttribute.toString()].value);
            } else  {
                setArrayIndex(stateRef.value.length);
                setAttributeLabel('');
                setAttributeType('undefined');
                setAttributeValue(undefined)
            }
        } else {
            if (selectedAttribute !== "") {
                const attributeRef = getAttribute(baseState, selectedScope, selectedAttribute, 0);
                setAttributeLabel(attributeRef.argument);
                setAttributeType(attributeRef.type);
                setAttributeValue(attributeRef.value);
            } else {
                setAttributeLabel('');
                setAttributeType('undefined');
                setAttributeValue(undefined);
            }
        }
    }

    function deleteScopeCallback(label) {

        const baseStateClone = cloneDeep(baseState);
        deleteAttribute(baseStateClone, selectedScope, label, -1);
        if (selectedScope === label)
            setSelectedScope(scopeList[0]);

        setBaseState(baseStateClone);
        setSelectedAttribute('');
    }

    function addAttributeCallback(e) {
        e.preventDefault();

        let baseStateClone = cloneDeep(baseState);
        const stateRef = getScope(baseStateClone, selectedScope, 0);
        let oldArrayIndex = cloneDeep(arrayIndex);

        if ((stateRef.type !== 'array') && (!checkValidLabel(attributeLabel)))
            return;

        if (stateRef.type === 'array') {
            if (stateRef.value.length === arrayIndex) {

                stateRef.value.push({
                    argument: (selectedScope + '_array_' + arrayIndex.toString()),
                    type: attributeType,
                    value: attributeValue
                });

                let newArrayIndex = arrayIndex + 1;
                setArrayIndex(newArrayIndex);
            }
        } else {
            stateRef.value.push({
                argument: attributeLabel,
                type: attributeType,
                value: attributeValue
            });
        }

        if ((attributeType === 'object') || (attributeType === 'array')) {

            let statePathClone;

            if (selectedScope === '') {
                if (stateRef.type === 'array') {
                    statePathClone = "[" + oldArrayIndex.toString() + "]";
                } else {
                    statePathClone = attributeLabel;
                }
            } else {
                if (stateRef.type === 'array') {
                    statePathClone = (selectedScope.slice()) + "[" + oldArrayIndex.toString() + "]";
                } else {
                    statePathClone = (selectedScope.slice()) + "." + attributeLabel;
                }

            }

            setSelectedScope(statePathClone);

            if (attributeType === 'array')
                setArrayIndex(0);
        }

        setBaseState(baseStateClone);
        setSelectedAttribute('');
    }

    function updateSelectedAttributeCallback(e) {
        e.preventDefault();

        const baseStateClone = cloneDeep(baseState);
        const attributeRef = getAttribute(baseStateClone, selectedScope, selectedAttribute, 0);

        if (getScope(baseStateClone, selectedScope, 0).type !== 'array')
            if ((attributeRef.argument !== attributeLabel) && (!checkValidLabel(attributeLabel)))
                return;

        attributeRef.argument = attributeLabel;
        if (attributeRef.type !== 'object') {
            attributeRef.type = attributeType;
            attributeRef.value = attributeValue;
        }

        setBaseState(baseStateClone);
        setSelectedAttribute('');
    }

    function deleteSelectedAttributeCallback(e) {
        e.preventDefault();

        let baseStateClone = cloneDeep(baseState);
        deleteAttribute(baseStateClone, selectedScope, selectedAttribute, 0);
        if (selectedScope === attributeLabel)
            setSelectedScope(scopeList[0]);

        setBaseState(baseStateClone);
        setSelectedAttribute('');
    }

    useEffect(() => {
        setScopeList(["", ...generateBaseList(baseState, "")]);

    }, [baseState]);

    useEffect(() => {
        setAttributeList(generateAttributeList());
        selectedAttributeChange();
    }, [scopeList]);

    useEffect(() => {
        setSelectedAttribute('');
    }, [attributeList])

    useEffect(() => {
        setAttributeList(generateAttributeList());
        setSelectedAttribute('');
        setAttributeLabel('');
    }, [selectedScope]);


    useEffect(() => {
        selectedAttributeChange();
    }, [selectedAttribute])

    if (baseState === undefined) {
        return <div>asd</div>
    }

    return (
        <div className ="create-object-tab-wrapper">
            <form>
                <div className="mb-3 input-group">
                    <span className="input-group-text">Selected scope</span>
                    <select
                        className="form-select"
                        id="create-object-select-object-key-input"
                        onChange={onSelectedScopeChangeCallback}
                        value={selectedScope}
                    >
                        {scopeList.map(objPath => {
                            return (
                                <option key={objPath} value={objPath}>{(objPath==="")?"(root)":objPath}</option>
                            )
                        })}
                    </select>
                    <button
                        disabled={selectedScope===""}
                        className="btn btn-danger"
                        onClick={e => {
                            e.preventDefault();
                            deleteScopeCallback(selectedScope);
                        }}
                    >
                        Delete
                    </button>
                </div>
                {
                    (getScope(baseState, selectedScope, 0).type === 'array')? (
                        <div className="mb-3 input-group">
                            <span className="input-group-text">Selected Index</span>
                            <select
                                className="form-select"
                                onChange ={onSelectedAttributeChangeCallback}
                                value ={selectedAttribute}
                            >
                                <option value={''}>
                                    --New Item ({getScope(baseState, selectedScope, 0).value.length})--
                                </option>
                                {
                                    (attributeList.length > 0) && (
                                        <optgroup label="Indecies">
                                            {
                                                attributeList.map(attribute => {
                                                    return (
                                                        <option key={attribute} value={attribute}>{attribute}</option>
                                                    );
                                                })
                                            }
                                        </optgroup>
                                    )
                                }
                            </select>
                            <button
                                className="btn btn-danger"
                                onClick={deleteSelectedAttributeCallback}
                                disabled={selectedAttribute===""}
                            >
                                Delete
                            </button>
                        </div>
                    ) : (
                        <div className="mb-3 input-group">
                            <span className="input-group-text">Selected Attribute</span>
                            <select
                                className="form-select"
                                id="create-attribute-select-object-key-input"
                                onChange={onSelectedAttributeChangeCallback}
                                value={selectedAttribute}
                            >
                                <option value=''>--New Attribute--</option>
                                {
                                    (attributeList.length > 0) && (
                                        <optgroup label="Attributes">
                                            {
                                                attributeList.map(attribute => {
                                                    return (
                                                        <option key={attribute} value={attribute}>{attribute}</option>
                                                    );
                                                })
                                            }
                                        </optgroup>
                                    )
                                }
                            </select>
                            <button
                                className="btn btn-danger"
                                onClick={deleteSelectedAttributeCallback}
                                disabled={selectedAttribute===""}
                            >
                                Delete
                            </button>
                        </div>
                    )
                }
                {
                    (getScope(baseState, selectedScope, 0).type !== 'array') && (
                        <>
                            <div className="input-group mb-3">
                                <span className="input-group-text">Key</span>
                                <input
                                    type="text"
                                    className="form-control"
                                    placeholder="key"
                                    value={attributeLabel}
                                    onChange={onAttributeLabelChangeCallback}
                                />
                            </div>
                            {(errorMessage !== '') && (
                                <div className="alert alert-danger" role="alert">
                                    {errorMessage}
                                </div>
                            )}
                        </>
                    )
                }
                <div className="input-group mb-3">
                    <span className="input-group-text">Type</span>
                    <ArgumentTypeSelector
                        id="create-object-type-selector-input"
                        type={attributeType}
                        onChangeCallback={onAttributeTypeChangeCallback}
                        disabled={((selectedAttribute !== '') && (attributeType === 'object'))}
                    />
                </div>
                <div className="input-group mb-3">
                    {
                        ((attributeType !== "object") && (attributeType !== "array")) && (
                            <>
                                <span className="input-group-text">Value</span>
                                <ArgumentDataFieldInput
                                    type={attributeType}
                                    value={attributeValue}
                                    onChangeCallback={onAttributeValueChangeCallback}
                                />
                            </>
                        )
                    }
                </div>
                {
                    (selectedAttribute === '')?
                        (
                            <button
                                className="btn btn-primary"
                                onClick={addAttributeCallback}
                            >
                                Add
                            </button>
                        ) : (
                            <button
                                className="btn btn-primary"
                                onClick={updateSelectedAttributeCallback}
                            >
                                Edit
                            </button>
                        )
                }
            </form>
            <div className="creat-object-object-viewer">
                <CollapsibleStateViewer stateData={baseState} />
            </div>
            <button
                className="btn btn-primary"
                onClick={() => onChangeCallback(baseState)}
            >
                Save & Exit
            </button>
        </div>
    );

}

function CollapsibleStateViewer({stateData}) {

    const [hidden, setHidden] = useState(false);

    function AttributeField(attribute) {
        switch(attribute.type) {
            case 'array':
                return <CollapsibleStateViewer stateData={attribute}/>
            case 'object':
                return <CollapsibleStateViewer stateData={attribute}/>
            case 'null':
            case 'undefined':
                return <pre>{attribute.type}</pre>
            case 'boolean':
            case 'string':
            case 'number':
                return <pre>{attribute.value.toString()}</pre>
            default:
                return <div></div>
        }
    }

    function generateAttributeComponent(attribute) {
        const checkForArray = attribute.argument.match(/_array_\d$/g)
        return (
            <li key={attribute.argument + "-" + attribute.type + "-"}>
                <span>{(checkForArray !== null)?checkForArray[0].charAt(checkForArray[0].length-1):attribute.argument}: </span> {AttributeField(attribute)}
            </li>
        );
    }

    if (stateData === undefined) {
        return <div>waiting for data</div>
    }

    return (
        <>
            <span>{(stateData.type === 'object')?"{":"["}</span>
            <button className ="btn" onClick={() => setHidden(!hidden)}> {(hidden)?"+":"-"} </button>
            {
                (hidden)? (
                    <span>{"}"}</span>
                ) : (
                    <>
                        <ul>
                            {
                                stateData.value.map(objData => generateAttributeComponent(objData))
                            }
                        </ul>
                        <div>{(stateData.type === 'object')?"}":"]"}</div>
                    </>
                )
            }

        </>

    );
}

function CollapsibleObject({objectData}) {

    const [hidden, setHidden] = useState(false);

    useEffect(() => {
        console.log('objectData: ', objectData);
    }, [objectData])

    function AttributeField(objData) {

        switch(objData.type) {
            case 'array':
                return <span></span>
            case 'object':
                return <CollapsibleObject objectData={objData.value}/>
            case 'null':
            case 'undefined':
                return <pre>{objData.type}</pre>
            case 'boolean':
            case 'string':
            case 'number':
                return <pre>{objData.value.toString()}</pre>
            default:
                return <div>Bruh</div>
        }
    }

    function generateObjectComponent(objData) {
        return (
            <li key={objData.argument + "-" + objData.type + "-"}>
                <span>{objData.argument}: </span> {AttributeField(objData)}
            </li>
        );
    }

    if (!Array.isArray(objectData.value)) {
        return <div>waiting for data</div>
    }

    return (
        <>
            <span>{"{"}</span>
            <button className ="btn" onClick={() => setHidden(!hidden)}> {(hidden)?"+":"-"} </button>
            {
                (hidden)? (
                    <span>{"}"}</span>
                ) : (
                    <>
                        <ul>
                            {
                                objectData.value.map(objData => generateObjectComponent(objData))
                            }
                        </ul>
                        <div>{"}"}</div>
                    </>
                )
            }

        </>

    );
}

export default ObjectCreationTab;
