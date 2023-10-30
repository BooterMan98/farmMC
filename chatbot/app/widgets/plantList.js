import React, { useEffect, useState } from 'react';

const PlantList = (msg) => {

  console.log(msg)

  if (msg.payload.newData.length == 0) return <> NO PLANTS AVAILABLE </>
  

  const plantList = msg.payload.newData.map(plant => 
  <li key={plant} > {plant} </li>
  )
  return (
      <ul>
        {plantList}
      </ul>
  );
};

export default PlantList;
