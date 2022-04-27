import React, {useEffect, useState} from 'react';
import {useNavigate} from "react-router-dom";
import {useSelector} from 'react-redux';
import 'Project/pages/LoadingPage/LoadingPage.scss';

function newProject(pathToProject) {
    return new Promise((doResolve, doReject) => {
        fetch('/api/new_project', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "pathToProject": pathToProject
            }),
        }).then(res => res.json()).then(data => {
            console.log(data);
            if (data.status === "OK") {
                doResolve(data);
            } else {
                doReject(data);
            }
        });
    });
}

function LoadingPage({}){
    const navigate = useNavigate();
    const projectPath = useSelector(state => state.project.path);
    const [socket, setSocket] = useState(null);
    const [socketMessage, setSocketMessage] = useState({"status": "IDLE"});
    const [socketMessages, setSocketMessages] = useState([]);
    const [cancelProcess, setCancelProcess] = useState(false);

    const processBarSteps = (step) => {
        switch (step) {
            case "ANALYZE_PROCESS_FILES":
                return [0, 80];
            case "ANALYZE_CLEAN_DEPENDENCY":
                return [80, 90];
            case "ANALYZE_COUNT_DEPENDENCY":
                return [90, 100];
            default:
                return 0;
        }
    }

    useEffect(() => {
        if (projectPath === "") {
            navigate("/");
        } else {
            setSocket(new WebSocket("ws://" + location.host + "/sock/new_project"));
        }

    }, []);

    useEffect(() => {
        if (socket !== null) {
            socket.addEventListener("message", ev => {
                setSocketMessage(JSON.parse(ev.data));
            });
        }

    }, [socket]);

    useEffect(() => {
        if (socketMessage["status"] === "OK") {
            if ("statusCode" in socketMessage) {
                if (socketMessage["statusCode"] === "WELCOME") {
                    newProject(projectPath).then(() => {
                        console.log("Opened!");
                    })
                } else if (socketMessage["statusCode"] === "ANALYZE_COMPLETE") {
                    navigate("/TestCreatorPage");
                }
            }
        } else if (socketMessage["status"] === "ERROR") {
            if ("statusCode" in socketMessage) {
                if (socketMessage["statusCode"] === "ANALYZE_ERR_CLIENT_STOP") {
                    navigate("/");
                }
            }
        }

        setSocketMessages([JSON.stringify(socketMessage), ...socketMessages]);

    }, [socketMessage]);
    return (
        <>
            <div className="container loading-page">
                <div className="container section-loader">
                    <h2>Opening project</h2>
                    <h4>{
                        cancelProcess &&
                            "Cancelling process..." ||
                        socketMessage["statusCode"] === "ANALYZE_PROCESS_FILES" &&
                            "Step 1/3: Analyzing files" ||
                        socketMessage["statusCode"] === "ANALYZE_CLEAN_DEPENDENCY" &&
                            "Step 2/3: Cleaning up dependency table" ||
                        socketMessage["statusCode"] === "ANALYZE_COUNT_DEPENDENCY" &&
                            "Step 3/3: Counting function dependencies" ||
                        "..."}</h4>
                    <div className="row">
                        <div className="col-md-2">
                            Status
                        </div>
                        <div className="col">
                            {socketMessage["message"]}
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-12">
                            <div className="progress loader-animation">
                                {!cancelProcess &&
                                    (socketMessage["statusCode"] === "ANALYZE_PROCESS_FILES" ||
                                    socketMessage["statusCode"] === "ANALYZE_CLEAN_DEPENDENCY" ||
                                    socketMessage["statusCode"] === "ANALYZE_COUNT_DEPENDENCY") && (() => {
                                        const progressPercent = processBarSteps(socketMessage["statusCode"])[0] +
                                            Math.trunc(
                                                (parseInt(socketMessage["currentNumber"]) /
                                                    parseInt(socketMessage["goalNumber"])) *
                                                (processBarSteps(socketMessage["statusCode"])[1] -
                                                    processBarSteps(socketMessage["statusCode"])[0])
                                            );
                                        return (<div
                                            className="progress-bar progress-bar-striped progress-bar-animated"
                                            role="progressbar"
                                            style={{"width" : progressPercent + "%"}}>
                                            {progressPercent}%
                                        </div>);
                                })() || (
                                    <div
                                        className="progress-bar progress-bar-striped progress-bar-animated"
                                        role="progressbar"
                                        style={{"width" : "0%"}}>...</div>
                                )}

                            </div>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-12 text-center">
                            <button
                                type="button"
                                className="btn btn-danger btn-sm"
                                onClick={() => {
                                    socket.send(JSON.stringify({
                                        "userAction": "ANALYZE_STOP"
                                    }))
                                    setCancelProcess(true);
                                }}
                                disabled={cancelProcess}
                            >Cancel</button>
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
}

export default LoadingPage;