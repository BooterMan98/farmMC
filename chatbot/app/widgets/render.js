import React, { useEffect, useState } from 'react';

const FarmRender = () => {
  const [imageUrl, setImageUrl] = useState('');

  useEffect(() => {
    fetch("")
      .then((res) => res.json())
      .then((data) => {
        setImageUrl(data.message);
      });
  }, []);

  return (
    <div>
      <img src={"https://placehold.co/300"} alt='A render of your farm' />
      pepe
    </div>
  );
};

export default FarmRender;
