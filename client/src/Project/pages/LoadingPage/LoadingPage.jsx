import React, {useEffect, useState} from 'react';
import {useNavigate} from "react-router-dom";
import {useSelector} from 'react-redux';

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
        }

        setSocketMessages([JSON.stringify(socketMessage), ...socketMessages]);

    }, [socketMessage]);
    return (
        <>
            <div>LoadingPage</div>
            <div>{projectPath}</div>
            <div>{socketMessage["statusCode"] === "ANALYZE_PROCESS_FILES" && (
                <span>{socketMessage["currentNumber"]} / {socketMessage["goalNumber"]}</span>
            )}</div>
            <ul className="list-group">
                {socketMessages.map((curMessage) =>
                        <li
                            className="list-group-item"
                            key={curMessage}>
                            {curMessage}
                        </li>
                    )
                }
            </ul>
        </>
    )
}

export default LoadingPage;