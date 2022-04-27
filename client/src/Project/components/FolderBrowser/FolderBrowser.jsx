import React from 'react';

/**
 * From https://icons.getbootstrap.com/icons/folder/
 * @returns {JSX.Element}
 * @constructor
 */
const IconFolder = () => {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
             className="icon bi bi-folder" viewBox="0 0 16 16">
            <path
                d="M.54 3.87.5 3a2 2 0 0 1 2-2h3.672a2 2 0 0 1 1.414.586l.828.828A2 2 0 0 0 9.828 3h3.982a2 2 0 0 1
                1.992 2.181l-.637 7A2 2 0 0 1 13.174 14H2.826a2 2 0 0 1-1.991-1.819l-.637-7a1.99 1.99 0 0 1
                .342-1.31zM2.19 4a1 1 0 0 0-.996 1.09l.637 7a1 1 0 0 0 .995.91h10.348a1 1 0 0 0 .995-.91l.637-7A1 1 0
                0 0 13.81 4H2.19zm4.69-1.707A1 1 0 0 0 6.172 2H2.5a1 1 0 0 0-1 .981l.006.139C1.72 3.042 1.95 3 2.19
                3h5.396l-.707-.707z"/>
        </svg>)
}

/**
 * From https://icons.getbootstrap.com/icons/folder-check/
 * @returns {JSX.Element}
 * @constructor
 */
const IconFolderProject = () => {
    return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor"
             className="icon bi bi-folder-check" viewBox="0 0 16 16">
            <path
                d="m.5 3 .04.87a1.99 1.99 0 0 0-.342 1.311l.637 7A2 2 0 0 0 2.826 14H9v-1H2.826a1 1 0 0
                1-.995-.91l-.637-7A1 1 0 0 1 2.19 4h11.62a1 1 0 0 1 .996 1.09L14.54 8h1.005l.256-2.819A2 2 0 0 0 13.81
                3H9.828a2 2 0 0 1-1.414-.586l-.828-.828A2 2 0 0 0 6.172 1H2.5a2 2 0 0 0-2 2zm5.672-1a1 1 0 0 1
                .707.293L7.586 3H2.19c-.24 0-.47.042-.683.12L1.5 2.98a1 1 0 0 1 1-.98h3.672z"/>
            <path
                d="M15.854 10.146a.5.5 0 0 1 0 .708l-3 3a.5.5 0 0 1-.707 0l-1.5-1.5a.5.5 0 0 1 .707-.708l1.146 1.147
                2.646-2.647a.5.5 0 0 1 .708 0z"/>
        </svg>)
}

const FolderBrowser = ({ fileListState, curDirState, isCurDirProjectState, setSubDir }) => {
    return (
        <>
            <div className="component-folder-browser">
                <div className="list-group section-top">
                    <div
                        className={isCurDirProjectState &&
                            "list-group-item list-group-item-success" ||
                            "list-group-item list-group-item-light"}
                        aria-current="true">
                        {isCurDirProjectState && <IconFolderProject /> || <IconFolder />}
                        {curDirState || "/"}
                    </div>
                    <a
                        href="#"
                        className="list-group-item list-group-item-action list-group-item-secondary"
                        onClick={() => {
                            setSubDir(curDirState + "/..")
                        }}><IconFolder />..</a>
                </div>
                <div className="container list-group section-browser-listing">
                    {fileListState.map((fileListItem) =>
                        (fileListItem["isDirectory"] && (
                            <a
                                href="#"
                                className={fileListItem["isProject"] &&
                                    "list-group-item list-group-item-success" ||
                                    "list-group-item list-group-item-action"}
                                key={fileListItem["fileName"]}
                                onClick={() => {
                                    setSubDir(fileListItem["subDir"] + "/" + fileListItem["fileName"])
                                }}>
                                {fileListItem["isProject"] && <IconFolderProject /> || <IconFolder />}
                                {fileListItem["subDir"] !== "/" && fileListItem["subDir"]}/{fileListItem["fileName"]}
                            </a>
                        )))
                    }
                </div>
            </div>
        </>
    );
};

export default FolderBrowser;