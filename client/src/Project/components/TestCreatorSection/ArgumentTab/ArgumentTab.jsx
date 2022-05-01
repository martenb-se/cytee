import React, {useEffect, useState} from 'react';
import {selectActiveFunction} from "../../../../reducers/activeFunctionSlice";
import {selectUnsavedActiveTest, updateArgumentList} from "../../../../reducers/activeTestInfoSlice";
import {useDispatch, useSelector} from "react-redux";

import ArgumentTypeSelector from "../../../../shared/components/ArgumentTypeSelector";
import ArgumentDataFieldInput from "../../../../shared/components/ArgumentInputValueSelector";
import ObjectDataFieldInput from "../ObjectDataFieldInput/ObjectDataFieldInput";

import cloneDeep from "lodash/cloneDeep";
import {isEmpty} from "lodash";

function ArgumentTab({label, addChildFunction, removeChildFunction}) {

    const activeFunction = useSelector(selectActiveFunction);
    const unsavedTest = useSelector(selectUnsavedActiveTest);
    const dispatch = useDispatch();

    const [activeChildTabs, setActiveChildTabs] = useState([]);

    function onChangeCallback(argumentData) {
        dispatch(updateArgumentList(argumentData));
    }

    useEffect(() => {
        console.log('activeChildTabs: ', activeChildTabs);
    }, [activeChildTabs])

    function onSubTabChangeCallback(objectData) {
        const argumentDataClone = cloneDeep(objectData);
        const activeChildTabsClone = cloneDeep(activeChildTabs);
        const childTabIndex = activeChildTabsClone.findIndex(tab => tab.label === objectData.argument + "-Object editor");
        activeChildTabsClone.splice(childTabIndex, 1);
        setActiveChildTabs(activeChildTabsClone);
        removeChildFunction(objectData.argument + "-Object editor");
        onChangeCallback(argumentDataClone);
    }

    function openSubTab(argumentData) {
        if (
            activeChildTabs.findIndex(
                tab => tab.label === (argumentData.argument + "-Object editor")
            ) === -1
        ) {
            const activeChildTabsClone = cloneDeep(activeChildTabs);
            activeChildTabsClone.push(argumentData.argument + "-Object editor");
            setActiveChildTabs(activeChildTabsClone);

            addChildFunction({
                initValue: argumentData,
                onObjectChangeCallback: onSubTabChangeCallback,
                parentLabel: "Argument List",
                label: argumentData.argument + "-Object editor"
            });
        }
    }

    function changeArgumentType(e, argumentData) {
        const argumentDataClone = cloneDeep(argumentData);
        argumentDataClone.type = e.target.value;
        switch(argumentDataClone.type) {
            case 'undefined':
            case 'null':
                delete argumentDataClone.value;
                break;
            case 'array':
                argumentDataClone.value = [];
                break;
            case 'boolean':
                argumentDataClone.value = false;
                break;
            case 'number':
                argumentDataClone.value = 0;
                break;
            case 'string':
                argumentDataClone.value = '';
                break;
            case 'object':
                argumentDataClone.value = [];
                break;
        }

        const activeChildTabsClone = cloneDeep(activeChildTabs);
        const activeChildTabsIndex = activeChildTabsClone.findIndex(tab => tab.label === (argumentData.argument + "-Object editor"))
        if (activeChildTabsIndex !== -1) {
            activeChildTabsClone.splice(activeChildTabsIndex, 1);
            setActiveChildTabs(activeChildTabsClone);
            removeChildFunction(argumentData.argument + "-Object editor");
        }
        onChangeCallback(argumentDataClone);
    }

    function changeArgumentValue(e, argumentData) {
        const argumentDataClone = cloneDeep(argumentData);
        argumentDataClone.value = e.target.value;
        onChangeCallback(argumentDataClone);
    }

    if (isEmpty(unsavedTest) ||
        (unsavedTest.moduleData === undefined) ||
        (unsavedTest.moduleData.argumentList === undefined)
    ) {
        return <div className ="test-creator-tab-empty">waiting...</div>
    }



    return (
        <div className="argument-tab-wrapper">
            <form>
                {
                    unsavedTest.moduleData.argumentList.map(argumentData => {
                        return (
                            <div className ="mb-3" key={argumentData.subFunctionName + '.' + argumentData.argument}>
                                <div className="argumentField-wrapper">
                                    <label
                                        className="form-label"
                                        htmlFor={argumentData.subFunctionName + "-" + argumentData.argument}
                                    >
                                        {argumentData.subFunctionName + ": " + argumentData.argument}
                                    </label>
                                    <div className="input-group">

                                        <ArgumentTypeSelector
                                            id={argumentData.subFunctionName + "-" + argumentData.argument}
                                            type={argumentData.type}
                                            onChangeCallback={e => changeArgumentType(e, argumentData)}
                                        />
                                        {(argumentData.type === 'object')?
                                            <button
                                                className="btn btn-secondary"
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    console.log('argumentData: ', argumentData);
                                                    openSubTab(argumentData);
                                                }}
                                            >
                                                Edit
                                            </button>
                                            :
                                            <ArgumentDataFieldInput
                                                type={argumentData.type}
                                                value={argumentData.value}
                                                onChangeCallback={e => changeArgumentValue(e, argumentData)}
                                            />
                                        }
                                    </div>
                                    {(argumentData.type === 'object') && (
                                        <div className="input-group">
                                            SHOW OBJECT HEAR!
                                        </div>
                                        )}
                                </div>
                            </div>
                        )
                    })
                }

            </form>
        </div>
    );
}

/*
function ArgumentField({argumentData, changeArgumentData}) {

    function changeArgumentType(e) {
        const argumentDataClone = cloneDeep(argumentData);
        argumentDataClone.type = e.target.value;
        switch(argumentDataClone.type) {
            case 'undefined':
            case 'null':
                delete argumentDataClone.value;
                break;
            case 'array':
                argumentDataClone.value = [];
                break;
            case 'boolean':
                argumentDataClone.value = false;
                break;
            case 'number':
                argumentDataClone.value = 0;
                break;
            case 'string':
                argumentDataClone.value = '';
                break;
            case 'object':
                argumentDataClone.value = {};
                break;
        }
        changeArgumentData(argumentDataClone);
    }

    function changeArgumentValue(e) {
        const argumentDataClone = cloneDeep(argumentData);
        argumentDataClone.value = e.target.value;
        changeArgumentData(argumentDataClone);
    }

    return (
        <div className="argumentField-wrapper">
            <label
                className="form-label"
                htmlFor={argumentData.subFunctionName + "-" + argumentData.argument}
            >
                {argumentData.subFunctionName + ": " + argumentData.argument}
            </label>
            <div className="input-group">
                <ArgumentTypeSelector id={argumentData.subFunctionName + "-" + argumentData.argument} type={argumentData.type} onChangeCallback={changeArgumentType} />
                <ArgumentDataFieldInput type={argumentData.type} value={argumentData.value} onChangeCallback={changeArgumentValue}/>
            </div>
        </div>
    )
}
*/


export default ArgumentTab;
/*
import React, {useState, useEffect, useContext} from 'react';
import {unsavedTestInfoContext} from "../TestCreatorSection";

// lodash helpers
import cloneDeep from "lodash/cloneDeep";

// components
import CustomTab from "../../../../shared/components/Tab";
import ArgumentTypeSelector from "../../../../shared/components/ArgumentTypeSelector";
import ArgumentDataFieldInput from "../../../../shared/components/ArgumentInputValueSelector";

function argumentsTabGenerator() {

    const [state, dispatch] = useContext(unsavedTestInfoContext);

    function updateArgument(argumentData) {
        dispatch({
            type: 'argumentList/changeArgument',
            payload: argumentData,
        });
    }

    return (
        <CustomTab label='Arguments'>
            <div>
                <h1>Arguments Tab</h1>
                <ul>
                    {state && state.moduleData && state.moduleData.argumentList &&
                        state.moduleData.argumentList.map( argumentData => {
                          return (
                              <li key={argumentData.subFunctionName + '.' + argumentData.argument}>
                                    <ArgumentField argumentData={argumentData} changeArgumentData={updateArgument}/>
                              </li>
                          )
                        })
                    }
                </ul>
            </div>
        </CustomTab>
    );
}

function ArgumentField({argumentData, changeArgumentData}) {

    function changeArgumentType(e) {
        const argumentDataClone = cloneDeep(argumentData);
        argumentDataClone.type = e.target.value;
        switch(argumentDataClone.type) {
            case 'undefined':
            case 'null':
                delete argumentDataClone.value;
                break;
            case 'array':
                argumentDataClone.value = [];
                break;
            case 'boolean':
                argumentDataClone.value = false;
                break;
            case 'number':
                argumentDataClone.value = 0;
                break;
            case 'string':
                argumentDataClone.value = '';
                break;
            case 'object':
                argumentDataClone.value = {};
                break;
        }
        changeArgumentData(argumentDataClone);
    }

    function changeArgumentValue(e) {
        const argumentDataClone = cloneDeep(argumentData);
        argumentDataClone.value = e.target.value;
        changeArgumentData(argumentDataClone);
    }

    return (
        <div className="argumentField-wrapper">
            <span>{argumentData.argument}</span>
            <ArgumentTypeSelector type={argumentData.type} onChangeCallback={changeArgumentType} />

            <ArgumentDataFieldInput type={argumentData.type} value={argumentData.value} onChangeCallback={changeArgumentValue}/>
        </div>
    )
}

function ArgumentDataFieldInput2({argumentData, changeArgumentData}) {

    function changeArgumentValue(e) {
        const argumentDataClone = cloneDeep(argumentData);
        argumentDataClone.value = e.target.value;
        changeArgumentData(argumentDataClone);
    }

    switch(argumentData.type) {
        case 'undefined':
        case 'null':
            return <input
                type="text"
                disabled
                value={argumentData.type}
            />
        case 'boolean':
            return (
                <select
                    className="form-select"
                    defaultValue={argumentData.value}
                    onChange={changeArgumentValue}
                >
                    <option value={false}>False</option>
                    <option value={true}>True</option>
                </select>
            )
        case 'number':
            return (
                <input
                    type ="number"
                    value={argumentData.value}
                    onChange={changeArgumentValue}
                />
            )
        case 'string':
            return <input
                type="text"
                onChange={changeArgumentValue}
                value={argumentData.value}
            />
        case 'object':
            return <ObjectCreator />
        default:
            return <div>[Input]</div>
    }
}

export function ObjectCreator() {

    const [tempObject, setTempObject] = useState({});

    const [label, setLabel] = useState('');
    const [type, setType] = useState('undefined');
    const [value, setValue] = useState('');

    useEffect(() => {
        switch(type) {
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
    }, [type])

    function createObjectView(tempObject) {
        console.log(tempObject);
        const keyList = Object.keys(tempObject);

        return keyList.map(key => {

            if (tempObject[key] === null){
                return <li>{key}: null</li>
            } else if (Array.isArray(tempObject[key])) {
                return <li>{key}: [Array]</li>
            }
            switch(typeof tempObject[key]) {

                case 'object':
                    return (
                        <details open>
                            <summary>{key}:{"{"}</summary>
                            <ul>
                                {createObjectView(tempObject[key])}
                            </ul>
                            {"}"}
                        </details>
                    );

                case 'boolean':
                case 'string':
                    return <li>{key}: {tempObject[key].toString()}</li>
                case 'undefined':
                    return <li>{key}: undefined</li>
                default:
                    return <li>{key}: [unable to detect type of value]</li>
            }
        });

    }

    function onTypeChangeCallback(e) {
        setType(e.target.value);
    }

    function onValueChangeCallback(payload) {
        console.log('payload: ', payload);
        setValue(payload);
    }

    function modifyObject() {
        const objectCopy = cloneDeep(tempObject);
        console.log(objectCopy);
        objectCopy[label] = value;
        setTempObject(objectCopy[label]);
    }

    if ((label === undefined) || (type === undefined)) {
        return <div>🍌🍌🍌🍌🍌🍌🍌🍌</div>
    }

    // TODO: Redo as form ???
    return (
        <div>
            <div>
                <div>
                    <span>Label: </span>
                    <input type ="text" value={label} onChange={e => setLabel(e.target.value)}/>
                </div>
                <div>
                    <span>Type: </span>
                    <ArgumentTypeSelector type={type} onChangeCallback={onTypeChangeCallback} />
                </div>
                <div>
                    <span>Value: </span>
                    <ArgumentDataFieldInput argumentData={{type: type, value: value}} changeArgumentData={onValueChangeCallback}/>

                </div>
                <button onClick={() => modifyObject()}>add</button>
            </div>
            <div>
                {"{"}
                <details open>
                    <summary>root</summary>
                    <ul>
                        {createObjectView(tempObject)}
                    </ul>

                </details>
                {"}"}
            </div>
        </div>
    )
}

export default argumentsTabGenerator;
*/