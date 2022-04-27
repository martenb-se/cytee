import React, {useEffect, useState, useLayoutEffect} from 'react';
import {useNavigate} from "react-router-dom";
import {useDispatch} from 'react-redux';
import {setPath} from "reducers/project/projectActions";
import FolderBrowser from "Project/components/FolderBrowser";
import 'Project/pages/ProjectSelectionPage/ProjectSelectionPage.scss';

function existingProjects() {
    return new Promise((doResolve, doReject) => {
        fetch('/api/get_existing_projects').
        then(res => res.json()).then(data => {
            if (data.status === "OK") {
                doResolve(data);
            } else {
                doReject(data);
            }
        });
    });
}

function listFiles(currentDirectory = "") {
    return new Promise((doResolve, doReject) => {
        fetch('/api/list_files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "subDirectory": currentDirectory
            }),
        }).then(res => res.json()).then(data => {
            if (data.status === "OK") {
                console.log(data);
                doResolve(data);
            } else {
                doReject(data);
            }
        });
    });
}

/**
 *
 * @returns {JSX.Element}
 * @constructor
 */
const ToolTip =
    ({subDir, fileListState, curDirState, isCurDirProjectState, previousProjectsState, openProjectCallback}) => {
    if(isCurDirProjectState) {
        return (<p>
            Now you can open the already existing project at <span className="badge bg-secondary">{curDirState}</span>
            by clicking the <button
                type="button"
                className="btn btn-success btn-sm"
                onClick={openProjectCallback}>
                Open Project
            </button> button here in this text or down below.
        </p>)
    } else {
        return (<p>
            Use the <span className="badge bg-secondary">Folder browser</span> below to create new projects or open
            already existing ones.
        </p>)
    }
}

function ProjectSelectionPage({}){
    const [subDir, setSubDir] = useState("");
    const [fileListState, setFileListState] = useState([]);
    const [curDirState, setCurDirState] = useState("");
    const [isCurDirProjectState, setIsCurDirProjectState] = useState("");
    const [previousProjectsState, setPreviousProjectsState] = useState([]);
    const navigate = useNavigate();
    const dispatch = useDispatch();

    const openProjectCallback = () => {
        dispatch(setPath(curDirState));
        navigate("/LoadingPage");
    }

    useEffect(() => {
        existingProjects().then((previousProjectInfo) => {
            setPreviousProjectsState(previousProjectInfo["existingProjects"]);
        })
    }, []);

    useEffect(() => {
        listFiles(subDir).then((fileListingInfo) => {
            setFileListState(fileListingInfo["fileList"]);
            setCurDirState(fileListingInfo["curDir"]);
            setIsCurDirProjectState(fileListingInfo["isCurDirProject"]);
        })

    }, [subDir]);

    return (
        <>
            <div className="container project-selection-page">
                <div className="row section-top">
                    <div className="col-6">
                        <h4>Previous projects</h4>
                        <div className="list-group top-item">
                            {previousProjectsState.map((previousProjectItem) =>
                                (
                                    <a
                                        href="#"
                                        className="list-group-item list-group-item-action"
                                        key={previousProjectItem}
                                        onClick={() => {
                                            setSubDir(previousProjectItem)
                                        }}>
                                        {previousProjectItem}
                                    </a>
                                ))
                            }
                        </div>
                    </div>
                    <div className="col-2">
                        <h4>Statistics</h4>
                        <div className="top-item">
                            <div className="item-statistics-pie"></div>
                        </div>
                    </div>
                    <div className="col">
                        <h4>Information</h4>
                        <div className="top-item">
                            <ToolTip
                                curDirState={curDirState}
                                isCurDirProjectState={isCurDirProjectState}
                                fileListState={fileListState}
                                previousProjectsState={previousProjectsState}
                                subDir={subDir}
                                openProjectCallback={openProjectCallback}/>
                        </div>
                    </div>
                </div>
                <div className="row section-folder-browser">
                    <div className="col">
                        <h4>Folder browser</h4>

                        <FolderBrowser
                            fileListState={fileListState}
                            curDirState={curDirState}
                            isCurDirProjectState={isCurDirProjectState}
                            setSubDir={setSubDir}/>
                    </div>
                </div>
                <form className="container section-form-project-confirmation">
                    {false && <div className="form-group">
                        <input className="form-control" readOnly value={curDirState || "/"} />
                    </div>}
                    <button
                        type="button"
                        className={isCurDirProjectState &&
                            "btn btn-success btn-lg col-12" ||
                            "btn btn-primary btn-lg col-12"}
                        onClick={openProjectCallback}
                    >{isCurDirProjectState && "Open Project" || "New Project"}</button>
                </form>
            </div>
        </>
    )
}

export default ProjectSelectionPage;