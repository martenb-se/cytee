import React, {useEffect, useState} from 'react';
import {useNavigate} from "react-router-dom";
import {useDispatch} from 'react-redux';
import {setPath} from "reducers/project/projectActions";

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
                doResolve(data);
            } else {
                doReject(data);
            }
        });
    });
}

function ProjectSelectionPage({}){
    const [subDir, setSubDir] = useState("");
    const [fileListState, setFileListState] = useState([]);
    const [curDirState, setCurDirState] = useState("");
    const navigate = useNavigate();
    const dispatch = useDispatch();

    useEffect(() => {
        listFiles(subDir).then((fileListingInfo) => {
            setFileListState(fileListingInfo["fileList"]);
            setCurDirState(fileListingInfo["curDir"]);
        })

    }, [subDir]);

    return (
        <>
            <div>ProjectSelectionPage</div>
            <div className="list-group">
                <a
                    href="#"
                    className="list-group-item list-group-item-action list-group-item-primary"
                    aria-current="true">{curDirState || "/"}</a>
                <a
                    href="#"
                    className="list-group-item list-group-item-action list-group-item-secondary"
                    onClick={() => {
                    setSubDir(curDirState + "/..")
                }}>..</a>
                {fileListState.map((fileListItem) =>
                    (fileListItem["isDirectory"] && (
                        <a
                            href="#"
                            className="list-group-item list-group-item-action"
                            key={fileListItem["fileName"]}
                            onClick={() => {
                                setSubDir(fileListItem["subDir"] + "/" + fileListItem["fileName"])
                            }}>
                            {fileListItem["subDir"]}/{fileListItem["fileName"]}
                        </a>
                    )))
                }
            </div>
            <button
                type="button"
                className="btn btn-primary btn-lg btn-block"
                onClick={() => {
                    dispatch(setPath(curDirState));
                    navigate("/LoadingPage");
                }}
            >Create New Project</button>
        </>
    )
}

export default ProjectSelectionPage;