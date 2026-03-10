import IngestURL from "../components/IngestURL";
import DocumentList from "../components/DocumentList";

export default function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <IngestURL />
      <hr />
      <DocumentList />
    </div>
  );
}