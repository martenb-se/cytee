import React, {useState, useEffect} from 'react';
import CustomTab from "../../../../shared/components/Tab";

const functionInfo = {
    pathToProject: "/path/to/project/src/",
    fileId: "shared/util/api",
    functionId: "func1",
    arguments: [{
        func1: [{
            "type": "Identifier",
            "name": "arg1"
        },
            {
                "type": "Identifier",
                "name": "arg2"
            },
            {
                "type": "ObjectPattern",
                "properties": [{
                    "type": "Property",
                    "key": {
                        "type": "Identifier",
                        "name": "objArg1"
                    },
                    "computed": false,
                    "value": {
                        "type": "Identifier",
                        "name": "objArg1"
                    },
                    "kind": "init",
                    "method": false,
                    "shorthand": true
                },
                    {
                        "type": "Property",
                        "key": {
                            "type": "Identifier",
                            "name": "objArg2"
                        },
                        "computed": false,
                        "value": {
                            "type": "Identifier",
                            "name": "objArg2"
                        },
                        "kind": "init",
                        "method": false,
                        "shorthand": true
                    }
                ]
            },
            {
                "type": "Identifier",
                "name": "arg3"
            },
            {
                "type": "ArrayPattern",
                "elements": [{
                    "type": "Identifier",
                    "name": "ArrArg1"
                },
                    {
                        "type": "Identifier",
                        "name": "ArrArg2"
                    }
                ]
            },
            {
                "type": "RestElement",
                "argument": {
                    "type": "Identifier",
                    "name": "rem"
                }
            }
        ]
    }],
    functionRange: [1, 3],
    functionHash: "asdasdjkhaskdjh",
    dependents: 24,
    dependencies: 10,
    numberOfTests: 90,
    exportInfo: "export",
    exportName: "db"
};

function parseFunctionArgs(args) {
    const argumentList = [];

    for (const argumentData of args) {
        switch(argumentData.type) {
            case 'Identifier':
                argumentList.push(argumentData.name);
                break;
            case 'Property':
                argumentList.push(argumentData.key.name)
                break;
            case 'ObjectPattern':
                const objRecList = parseFunctionArgs(argumentData.properties);
                argumentList.push(...objRecList);
                break;
            case 'ArrayPattern':
                const arrRecList = parseFunctionArgs(argumentData.elements);
                argumentList.push(...arrRecList);
                break;
            case 'RestElement':
                argumentList.push('RestElement');
                break;
            default:
                break;
        }
    }
    return argumentList;
}

function parseFunction(args) {
    const fullArgumentList = [];
    for (const func of args) {
        const funcName = Object.keys(func)[0];
        const argList = parseFunctionArgs(func[funcName]);
        fullArgumentList.push({functionName: funcName, arguments: argList});
    }
    return fullArgumentList;
}

function ArgumentTab(props) {

    // Get the function info of the currently active function.



    const [argumentList, setArgumentList] = useState(undefined);

    // Generate a list of only the arguments from the arguments attribute of the function info.

    useEffect(() => {
        // TODO: Have to handle cases where argument list haven't been set.
        // TODO: Not the best solution as this has to be recomputed each time the component is reloaded.
        setArgumentList(parseFunction(functionInfo.arguments));

    }, [])
    console.log(argumentList);
    return (
        <CustomTab tabName={'Arguments'}>
            <div>
                {argumentList && argumentList.map(funcData => {
                    return (<>
                        <span>{funcData.functionName}</span>
                        <ul>
                            {
                                funcData.arguments.map(argName => {
                                    return (
                                        <>
                                            <ArgumentAssignmentTab argName={argName}/>
                                        </>
                                    )
                                })
                            }
                        </ul>
                    </>)
                    })
                }
            </div>
        </CustomTab>
    );
}

function ArgumentAssignmentTab({setTestArgument, argName}) {
    const [argumentName, setArgumentName] = useState('');
    const [argumentType, setArgumentType] = useState('');
    const [argumentValue, setArgumentValue] = useState('');

    useEffect(() => {
        setArgumentName(argName);
    }, []);

    function changeArgumentType(e) {
        console.log(e.target.value);
        setArgumentType(e.target.value);
    }

    return (
        <div className="argumentAssignment-wrapper">
            <span className="argumentAssignment-name">{argumentName}</span>
            <select value={argumentType} onChange={changeArgumentType}>
                <option value={'array'}>Array</option>
                <option value={'boolean'}>Boolean</option>
                <option value={'null'}>Null</option>
                <option value={'number'}>Number</option>
                <option value={'object'}>Object</option>
                <option value={'string'}>String</option>
                <option value={'undefined'}>Undefined</option>
            </select>
            <input type="text" />
        </div>
    )

}

export default ArgumentTab;