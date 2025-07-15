// Genesis Browser Viewer Module with Enhanced Debugging
export class GenesisLiveViewer {
    constructor(presignedUrl, containerId = 'dcv-display') {
        this.displayLayoutRequested = false;
        this.presignedUrl = presignedUrl;
        this.containerId = containerId;
        this.connection = null;
        this.desiredWidth = 1600;
        this.desiredHeight = 900;
        console.log('[GenesisLiveViewer] Initialized with URL:', presignedUrl);
    }

    httpExtraSearchParamsCallBack(method, url, body, returnType) {
        console.log('[GenesisLiveViewer] httpExtraSearchParamsCallBack called:', { method, url, returnType });
        const parsedUrl = new URL(this.presignedUrl);
        const params = parsedUrl.searchParams;
        console.log('[GenesisLiveViewer] Returning auth params:', params.toString());
        return params;
    }
    
    displayLayoutCallback(serverWidth, serverHeight, heads) {
        console.log(`[GenesisLiveViewer] Display layout callback: ${serverWidth}x${serverHeight}`);
        
        const display = document.getElementById(this.containerId);
        display.style.width = `${this.desiredWidth}px`;
        display.style.height = `${this.desiredHeight}px`;

        if (this.connection) {
            console.log(`[GenesisLiveViewer] Requesting display layout: ${this.desiredWidth}x${this.desiredHeight}`);
            // Only request display layout once
            if (!this.displayLayoutRequested) {
                console.log('inside this method');
                this.connection.requestDisplayLayout([{
                name: "Main Display",
                rect: {
                    x: 0,
                    y: 0,
                    width: this.desiredWidth,
                    height: this.desiredHeight
                },
                primary: true
                }]);

                this.displayLayoutRequested = true;
            }
        }
    }

    async connect() {
        return new Promise((resolve, reject) => {
            if (typeof dcv === 'undefined') {
                reject(new Error('DCV SDK not loaded'));
                return;
            }

            console.log('[GenesisLiveViewer] DCV SDK loaded, version:', dcv.version || 'Unknown');
            console.log('[GenesisLiveViewer] Available DCV methods:', Object.keys(dcv));
            console.log('[GenesisLiveViewer] Presigned URL:', this.presignedUrl);
            
            // Set debug logging
            if (dcv.setLogLevel) {
                dcv.setLogLevel(dcv.LogLevel.DEBUG);
                console.log('[GenesisLiveViewer] DCV log level set to DEBUG');
            }

            console.log('[GenesisLiveViewer] Starting authentication...');
            
            dcv.authenticate(this.presignedUrl, {
                promptCredentials: () => {
                    console.warn('[GenesisLiveViewer] DCV requested credentials - should not happen with presigned URL');
                },
                error: (auth, error) => {
                    console.error('[GenesisLiveViewer] DCV auth error:', error);
                    console.error('[GenesisLiveViewer] Error details:', {
                        message: error.message || error,
                        code: error.code,
                        statusCode: error.statusCode,
                        stack: error.stack
                    });
                    reject(error);
                },
                success: (auth, result) => {
                    console.log('[GenesisLiveViewer] DCV auth success:', result);
                    if (result && result[0]) {
                        const { sessionId, authToken } = result[0];
                        console.log('[GenesisLiveViewer] Session ID:', sessionId);
                        console.log('[GenesisLiveViewer] Auth token received:', authToken ? 'Yes' : 'No');
                        this.connectToSession(sessionId, authToken, resolve, reject);
                    } else {
                        console.error('[GenesisLiveViewer] No session data in auth result');
                        reject(new Error('No session data in auth result'));
                    }
                },
                httpExtraSearchParams: this.httpExtraSearchParamsCallBack.bind(this)
            });
        });
    }

    connectToSession(sessionId, authToken, resolve, reject) {
        console.log('[GenesisLiveViewer] Connecting to session:', sessionId);
        
        const connectOptions = {
            url: this.presignedUrl,
            sessionId: sessionId,
            authToken: authToken,
            divId: this.containerId,
            baseUrl: "/static/dcvjs",
            callbacks: {
                firstFrame: () => {
                    console.log('[GenesisLiveViewer] First frame received!');
                    resolve(this.connection);
                },
                error: (error) => {
                    console.error('[GenesisLiveViewer] Connection error:', error);
                    reject(error);
                },
                httpExtraSearchParams: this.httpExtraSearchParamsCallBack.bind(this),
                displayLayout: this.displayLayoutCallback.bind(this)
            }
        };
        
        console.log('[GenesisLiveViewer] Connect options:', connectOptions);
        
        dcv.connect(connectOptions)
        .then(connection => {
            console.log('[GenesisLiveViewer] Connection established:', connection);
            this.connection = connection;
        })
        .catch(error => {
            console.error('[GenesisLiveViewer] Connect failed:', error);
            reject(error);
        });
    }

    setDisplaySize(width, height) {
        this.desiredWidth = width;
        this.desiredHeight = height;
        
        if (this.connection) {
            this.displayLayoutCallback(0, 0, []);
        }
    }

    disconnect() {
        if (this.connection) {
            this.connection.disconnect();
            this.connection = null;
        }
    }
}