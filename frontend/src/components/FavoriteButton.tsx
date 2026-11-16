import { StarFilled, StarOutlined } from '@ant-design/icons';
import { Button, Tooltip } from 'antd';

export default function FavoriteButton({ active, loading, onClick }: {
  active: boolean; loading?: boolean; onClick: () => void;
}) {
  return (
    <Tooltip title={active ? 'Remove from favorites' : 'Add to favorites'}>
      <Button
        type="text"
        className={active ? 'favorite active' : 'favorite'}
        icon={active ? <StarFilled /> : <StarOutlined />}
        loading={loading}
        onClick={(event) => { event.stopPropagation(); onClick(); }}
        aria-label={active ? 'Remove from favorites' : 'Add to favorites'}
      />
    </Tooltip>
  );
}

