import React, {useContext, useEffect, useState} from 'react';
import {selectActiveFunction} from "../../../../reducers/activeFunctionSlice";
import {selectUnsavedActiveTest, updateArgumentList} from "../../../../reducers/activeTestInfoSlice";
import {useDispatch, useSelector} from "react-redux";

import ArgumentTypeSelector from "../../../../shared/components/ArgumentTypeSelector";
import ArgumentDataFieldInput from "../../../../shared/components/ArgumentInputValueSelector";
import ObjectDataFieldInput from "../ObjectDataFieldInput/ObjectDataFieldInput";

import {CollapsibleStateViewer} from "../objectCreationTab/ObjectCreationTab";

import cloneDeep from "lodash/cloneDeep";
import {isEmpty} from "lodash";
import {localTabGroupContext} from "../TestCreatorSection";

import './ArgumentTab.scss';

function ArgumentTab({label, addChildFunction, removeChildFunction}) {

    const activeFunction = useSelector(selectActiveFunction);
    const unsavedTest = useSelector(selectUnsavedActiveTest);
    const dispatch = useDispatch();

    const [localTabState, localTabDispatch] = useContext(localTabGroupContext);

    function onChangeCallback(argumentData) {
        dispatch(updateArgumentList(argumentData));
    }

    function onSubTabChangeCallback(objectData) {
        const argumentDataClone = cloneDeep(objectData);
        //removeChildFunction(objectData.argument);
        localTabDispatch({
            type: 'removeChildTab',
            payload: objectData.argument,
        });
        onChangeCallback(argumentDataClone);
    }

    function openSubTab(argumentData) {
        localTabDispatch({
            type: 'addChildTab',
            payload: {
                initValue: argumentData,
                onObjectChangeCallback: onSubTabChangeCallback,
                parentEventKey: "argumentList",
                eventKey: argumentData.argument,
                title: argumentData.argument + "-Object editor"
            }
        });
    }

    function onEdit(argumentData) {
        localTabDispatch({
            type: 'addChildTab',
            payload: {
                initValue: argumentData,
                onObjectChangeCallback: onSubTabChangeCallback,
                parentEventKey: "argumentList",
                eventKey: argumentData.argument,
                title: argumentData.argument + " - editor"
            }
        });
    }

    function changeArgumentType(e, argumentData) {
        const argumentDataClone = cloneDeep(argumentData);
        if ((argumentDataClone.type === 'object') || (argumentDataClone.type === 'array')) {
            localTabDispatch({
                type: 'removeChildTab',
                payload: argumentData.argument,
            });
        }
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
                                        <ArgumentDataFieldInput
                                            argumentData={argumentData}
                                            onChangeCallback={e => changeArgumentValue(e, argumentData)}
                                            disabled={false}
                                            onEdit={onEdit}
                                        />

                                    </div>
                                    {(argumentData.type === 'object' || argumentData.type === 'array') &&
                                        <CollapsibleStateViewer stateData={argumentData}/>
                                    }
                                </div>
                            </div>
                        )
                    })
                }

            </form>
        </div>
    );
}

export default ArgumentTab;