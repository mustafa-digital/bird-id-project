// src/components/ResultsList.jsx

function ResultsList({ results }) {
    if (results.length == 0) {
        return <p className="empty-state">No species detected</p>;
    }

  return (
        <ul className="space-y-4">
            {results.map((r) => {
                return (
                    <li
                        key={r.id}
                        className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
                    >
                        <div className="mb-2 flex items-center justify-between">
                            <span className="text-xs font-medium uppercase tracking-wide text-gray-500">
                                {r.timestamp.toLocaleTimeString()}
                            </span>
                        </div>

                        {r.predictions.length === 0 ? (
                            <span className="text-sm text-gray-500">
                                No species detected
                            </span>
                        ) : (
                            <ul className="space-y-2">
                                {r.predictions.map((p) => {
                                    return (
                                        <li
                                            key={p.species_code}
                                            className="flex flex-col items-start justify-between gap-2 sm:flex-row sm:items-center"
                                        >
                                            <span className="text-sm text-gray-800">
                                                {p.species_name} — {(p.confidence * 100).toFixed(1)}%
                                            </span>
                                        </li>
                                    )
                                })}
                            </ul>
                        )}
                    </li>
                )
            })}
        </ul>
    );
}

export default ResultsList;