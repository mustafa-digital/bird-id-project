import { useState } from 'react'
import RecordButton from "./components/RecordButton"
import FileUpload from './components/FileUpload';
import ResultsList from './components/ResultsList';
import ChatPanel from './components/ChatPanel';

function App() {
    const [results, setResults] = useState([]);
    const [error, setError] = useState(null);
    // const [chatPanelOpen, setChatPanelOpen] = useState(false);

    const handlePrediction = (predictions) => {
        setResults(() => [
            { id: crypto.randomUUID(), timestamp: new Date(), ...predictions }
        ]);
    };

    const handleError = (message) => {
        setError(message);
        setTimeout(() => setError(null), 4000)
    };

    return (
        <div className="min-h-screen bg-gray-50 text-gray-900">
            <div className="mx-auto max-w-3xl px-4 py-8">
                <header className="mb-6">
                    <h1 className="text-2xl font-semibold tracking-tight text-gray-900">
                        Bird Song Identifier
                    </h1>
                </header>

                <section className="mb-6">
                    <div className="flex flex-col gap-3 sm:flex-row">
                        <RecordButton onPrediction={handlePrediction} onError={handleError} />
                        <FileUpload onPrediction={handlePrediction} onError={handleError} />
                    </div>
                </section>

                {error && (
                    <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
                        {error}
                    </div>
                )}

                <ResultsList results={results} />
                <ChatPanel />

            </div>
        </div>
    );
}

export default App
