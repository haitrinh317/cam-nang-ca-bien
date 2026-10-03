import BiologyDashboard from '../BiologyDashboard'
import type { BiologyData } from '../BiologyDashboard'

interface SinhhocTabProps {
  bio: BiologyData | null
  speciesId: string
  collectionId: string | null
}

export default function SinhhocTab({ bio, speciesId, collectionId }: SinhhocTabProps) {
  return (
    <div
      id="tab-panel-sinhhoc"
      role="tabpanel"
      aria-labelledby="tab-sinhhoc"
      className="detail-tab-panel active"
    >
      {bio
        ? <BiologyDashboard bio={bio} speciesId={speciesId} collectionId={collectionId} />
        : <p className="specimen__empty">Chưa có dữ liệu sinh học cho loài này.</p>
      }
    </div>
  )
}
