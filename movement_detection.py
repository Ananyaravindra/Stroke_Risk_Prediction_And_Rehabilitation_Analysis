import ssl
import streamlit as st
import streamlit.components.v1 as components

# Configure page and SSL
st.set_page_config(page_title="Movement Analysis", page_icon="📹")
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def movement_analysis_interface():
    """Exercise Form Analysis using Camera"""
    st.subheader("📹 Exercise Form Analysis")
    
    # Add error handling and status messages
    st.info("Attempting to initialize camera interface...")
    
    components.html(
        """
        <!-- Add required libraries -->
        <script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.11.0/dist/tf.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@tensorflow-models/posenet@2.2.2/dist/posenet.min.js"></script>

        <div class="exercise-analyzer">
            <div id="error-messages" style="color: red;"></div>
            <div id="status-messages" style="color: blue;"></div>
            
            <div style="margin-bottom: 1rem;">
                <h3>Exercise Form Analysis</h3>
                <p>Position yourself in front of the camera and perform the exercise.</p>
            </div>
            
            <div style="display: flex; gap: 1rem;">
                <div style="flex: 1; border: 1px solid #ddd; padding: 1rem; border-radius: 8px;">
                    <video id="webcam" style="width: 100%; border-radius: 8px;" autoplay playsinline></video>
                    <canvas id="canvas" style="display: none;"></canvas>
                </div>
                
                <div style="flex: 1; border: 1px solid #ddd; padding: 1rem; border-radius: 8px;">
                    <h4>Analysis Results</h4>
                    <div id="analysis-results">
                        <p>Exercise: <span id="current-exercise">Not started</span></p>
                        <p>Form Score: <span id="form-score">-</span></p>
                        <p>Repetitions: <span id="rep-count">0</span></p>
                        <div id="feedback"></div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 1rem;">
                <button id="startBtn" onclick="startAnalysis()" 
                    style="padding: 0.5rem 1rem; background: #4CAF50; color: white; 
                           border: none; border-radius: 4px; cursor: pointer; margin-right: 1rem;">
                    Start Analysis
                </button>
                <select id="exerciseSelect" style="padding: 0.5rem; border-radius: 4px;">
                    <option value="arm-raise">Arm Raises</option>
                    <option value="leg-lift">Leg Lifts</option>
                    <option value="balance">Balance Exercise</option>
                </select>
            </div>
        </div>

        <script>
            let webcam, poseNet, isAnalyzing = false;
            let repCount = 0;
            let exerciseState = {
                armRaise: { count: 0, lastAngle: null, upwardPhase: false },
                legLift: { count: 0, lastAngle: null, upwardPhase: false },
                balance: { count: 0, startTime: null, totalTime: 0 }
            };

            // Log status messages
            function logStatus(message) {
                const statusDiv = document.getElementById('status-messages');
                statusDiv.innerHTML += `<div>${message}</div>`;
                console.log(message);
            }

            // Log errors
            function logError(error) {
                const errorDiv = document.getElementById('error-messages');
                errorDiv.innerHTML += `<div>Error: ${error}</div>`;
                console.error(error);
            }

            function updateFeedback(message, type = 'info') {
                const feedback = document.getElementById('feedback');
                feedback.textContent = message;
                feedback.style.backgroundColor = type === 'error' ? '#ffebee' : 
                                               type === 'success' ? '#e8f5e9' : '#e3f2fd';
            }

            async function initializeCamera() {
                try {
                    logStatus("Requesting camera permission...");
                    const stream = await navigator.mediaDevices.getUserMedia({ 
                        video: { 
                            width: 640, 
                            height: 480,
                            facingMode: 'user'
                        } 
                    });
                    
                    const video = document.getElementById('webcam');
                    video.srcObject = stream;
                    logStatus("Camera initialized successfully!");
                    
                    return new Promise((resolve) => {
                        video.onloadedmetadata = () => {
                            video.play();
                            resolve(video);
                        };
                    });
                } catch (error) {
                    logError(`Camera initialization failed: ${error.message}`);
                    throw error;
                }
            }

            async function loadPoseNet() {
                try {
                    logStatus("Loading PoseNet...");
                    if (typeof posenet === 'undefined') {
                        throw new Error('PoseNet library not loaded');
                    }
                    const net = await posenet.load({
                        architecture: 'MobileNetV1',
                        outputStride: 16,
                        inputResolution: { width: 640, height: 480 },
                        multiplier: 0.75
                    });
                    logStatus("PoseNet loaded successfully!");
                    return net;
                } catch (error) {
                    logError(`Failed to load PoseNet: ${error.message}`);
                    throw error;
                }
            }

            function calculateAngle(p1, p2, p3) {
                const radians = Math.atan2(p3.y - p2.y, p3.x - p2.x) -
                              Math.atan2(p1.y - p2.y, p1.x - p2.x);
                let angle = Math.abs(radians * 180.0 / Math.PI);
                if (angle > 180.0) { angle = 360 - angle; }
                return angle;
            }

            function analyzeArmRaise(keypoints) {
                const leftShoulder = keypoints.find(k => k.part === 'leftShoulder');
                const leftElbow = keypoints.find(k => k.part === 'leftElbow');
                const leftWrist = keypoints.find(k => k.part === 'leftWrist');
                
                if (leftShoulder && leftElbow && leftWrist) {
                    const angle = calculateAngle(
                        leftShoulder.position,
                        leftElbow.position,
                        leftWrist.position
                    );
                    
                    let formScore = 0;
                    if (angle > 160) {
                        formScore = 100;
                        updateFeedback("Perfect form!", "success");
                    } else if (angle > 140) {
                        formScore = 80;
                        updateFeedback("Good form!", "success");
                    } else if (angle > 120) {
                        formScore = 60;
                        updateFeedback("Raise your arms a bit higher");
                    } else {
                        formScore = 40;
                        updateFeedback("Try to raise your arms higher");
                    }
                    
                    document.getElementById('form-score').textContent = formScore + '%';
                    
                    // Rep counting logic
                    if (angle > 150 && !exerciseState.armRaise.upwardPhase) {
                        exerciseState.armRaise.upwardPhase = true;
                    } else if (angle < 60 && exerciseState.armRaise.upwardPhase) {
                        exerciseState.armRaise.count++;
                        exerciseState.armRaise.upwardPhase = false;
                        document.getElementById('rep-count').textContent = exerciseState.armRaise.count;
                    }
                }
            }

            function analyzeLegLift(keypoints) {
                const leftHip = keypoints.find(k => k.part === 'leftHip');
                const leftKnee = keypoints.find(k => k.part === 'leftKnee');
                const leftAnkle = keypoints.find(k => k.part === 'leftAnkle');
                
                if (leftHip && leftKnee && leftAnkle) {
                    const angle = calculateAngle(
                        leftHip.position,
                        leftKnee.position,
                        leftAnkle.position
                    );
                    
                    let formScore = 0;
                    if (angle > 150) {
                        formScore = 100;
                        updateFeedback("Perfect leg lift!", "success");
                    } else if (angle > 130) {
                        formScore = 80;
                        updateFeedback("Good form!", "success");
                    } else if (angle > 110) {
                        formScore = 60;
                        updateFeedback("Lift your leg higher");
                    } else {
                        formScore = 40;
                        updateFeedback("Try to lift your leg higher");
                    }
                    
                    document.getElementById('form-score').textContent = formScore + '%';
                    
                    // Rep counting logic
                    if (angle > 130 && !exerciseState.legLift.upwardPhase) {
                        exerciseState.legLift.upwardPhase = true;
                    } else if (angle < 90 && exerciseState.legLift.upwardPhase) {
                        exerciseState.legLift.count++;
                        exerciseState.legLift.upwardPhase = false;
                        document.getElementById('rep-count').textContent = exerciseState.legLift.count;
                    }
                }
            }

            async function detectPose() {
                if (!isAnalyzing) return;

                try {
                    const pose = await poseNet.estimateSinglePose(webcam, {
                        flipHorizontal: true
                    });

                    if (pose.score > 0.2) {
                        const exercise = document.getElementById('exerciseSelect').value;
                        switch(exercise) {
                            case 'arm-raise':
                                analyzeArmRaise(pose.keypoints);
                                break;
                            case 'leg-lift':
                                analyzeLegLift(pose.keypoints);
                                break;
                        }
                    }

                    if (isAnalyzing) {
                        requestAnimationFrame(detectPose);
                    }
                } catch (error) {
                    logError(`Pose detection error: ${error.message}`);
                }
            }

            async function startAnalysis() {
                try {
                    if (!isAnalyzing) {
                        // Reset state
                        exerciseState = {
                            armRaise: { count: 0, lastAngle: null, upwardPhase: false },
                            legLift: { count: 0, lastAngle: null, upwardPhase: false },
                            balance: { count: 0, startTime: null, totalTime: 0 }
                        };
                        document.getElementById('rep-count').textContent = '0';
                        document.getElementById('form-score').textContent = '-';
                        
                        // Initialize camera and PoseNet
                        webcam = await initializeCamera();
                        if (!poseNet) {
                            poseNet = await loadPoseNet();
                        }
                        
                        isAnalyzing = true;
                        document.getElementById('startBtn').textContent = 'Stop Analysis';
                        document.getElementById('current-exercise').textContent = 
                            document.getElementById('exerciseSelect').value;
                        
                        detectPose();
                        updateFeedback("Analysis started. Perform the exercise.");
                    } else {
                        isAnalyzing = false;
                        document.getElementById('startBtn').textContent = 'Start Analysis';
                        updateFeedback("Analysis stopped.");
                    }
                } catch (error) {
                    logError(`Failed to start analysis: ${error.message}`);
                    updateFeedback("Failed to start analysis. Please refresh and try again.", "error");
                }
            }

            // Initialize the system
            logStatus("System initialized. Click Start to begin analysis.");
            updateFeedback("Select an exercise and click Start to begin");
        </script>
        """,
        height=700,
    )

    # Add Streamlit status messages
    st.markdown("---")
    st.markdown("""
    ### Troubleshooting Tips:
    1. Make sure you allow camera access when prompted
    2. Check if your camera is properly connected
    3. Try refreshing the page if the camera doesn't initialize
    4. Make sure you're using a modern browser (Chrome/Firefox recommended)
    5. Stand at a distance where your full body is visible
    6. Ensure good lighting in the room
    """)

if __name__ == "__main__":
    movement_analysis_interface()