import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const TILE_SIZE = 8;
const GAP = 0.75; 
const STRIDE = TILE_SIZE + GAP; 
const ROAD_HEIGHT = 0.12;
const ROAD_COLOR = 0x00f3ff;
const animatingTiles = [];
const animatingRoads = [];
const scene = new THREE.Scene();
const existingRoads = new Set();
const existingDistricts = new Set();

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(10, 10, 10);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.maxPolarAngle = Math.PI / 2 - 0.05;
controls.update();

scene.add(new THREE.AmbientLight(0xffffff, 2));
const ws = new WebSocket('ws://127.0.0.1:8765');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
};

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

const routerGroup = new THREE.Group();

const router = new THREE.Mesh(
    new THREE.OctahedronGeometry(2),
    new THREE.MeshBasicMaterial({color:  0xffb700})
);

const routerEdges = new THREE.LineSegments(
  new THREE.EdgesGeometry(router.geometry),
  new THREE.LineBasicMaterial({ color: 0xffffff }) 
);

routerGroup.add(router);
routerGroup.add(routerEdges);
routerGroup.position.set(0, 2.5, 0);

function getGridPosition(index) {
  const ring = Math.ceil((Math.sqrt(index + 2) - 1) / 2);
  const firstIndexInRing = 4 * (ring - 1) * ring;
  const offset = index - firstIndexInRing;
  const side = ring * 2;

  let x;
  let z;
  if (offset < side) {
    x = -ring + 1 + offset;
    z = -ring;
  } else if (offset < side * 2) {
    x = ring;
    z = -ring + 1 + offset - side;
  } else if (offset < side * 3) {
    x = ring - 1 - offset + side * 2;
    z = ring;
  } else {
    x = -ring;
    z = ring - 1 - offset + side * 3;
  }

  return { 
    gx : x,
    gz : z,
    x: x * STRIDE,
    z: z * STRIDE };

};

function addRoad(key, centerX, centerZ, width, depth) {
  if (existingRoads.has(key)) {
    return;
  }

  const road = new THREE.Mesh(
    new THREE.BoxGeometry(width, ROAD_HEIGHT, depth),
    new THREE.MeshBasicMaterial({ color: ROAD_COLOR })
  );
  road.position.set(centerX, 0.06, centerZ);
  road.scale.set(width > depth ? 0.001 : 1, 1, width > depth ? 1 : 0.001);
  road.userData.animating = true;
  scene.add(road);
  animatingRoads.push(road);
  existingRoads.add(key);
}

function createRoadSegment(x1, z1, x2, z2) {
    const key = `${x1},${z1}->${x2},${z2}`;
    const reverse_key = `${x2},${z2}->${x1},${z1}`;

    if (existingRoads.has(key) || existingRoads.has(reverse_key)){
        return
    };

  const horizontal = z1 === z2;
  const centerX = (x1 + x2) / 2;
  const centerZ = (z1 + z2) / 2;
  const width = horizontal ? GAP : STRIDE;
  const depth = horizontal ? STRIDE : GAP;

  addRoad(key, centerX, centerZ, width, depth);
}

function createRouterRoad(x, z) {
  const key = `router->${x},${z}`;
  const horizontal = z === 0;
  const direction = horizontal ? Math.sign(x) : Math.sign(z);
  const length = GAP;
  const centerDistance = TILE_SIZE / 2 + length / 2;
  const centerX = horizontal ? direction * centerDistance : 0;
  const centerZ = horizontal ? 0 : direction * centerDistance;
  const width = horizontal ? length : STRIDE;
  const depth = horizontal ? STRIDE : length;

  addRoad(key, centerX, centerZ, width, depth);

};

function spawnDistrictTile(processName, index) {
  const pos = getGridPosition(index);
  const districtGroup = new THREE.Group();
  
  districtGroup.position.set(pos.x, -15, pos.z);

  districtGroup.userData = {
    targetY: 0,
    animating: true
  };

  animatingTiles.push(districtGroup); 

  const ground = new THREE.Mesh(
    new THREE.BoxGeometry(TILE_SIZE, 0.1, TILE_SIZE),
    new THREE.MeshBasicMaterial({ color: 0x0a0a12 })
  );

  const groundEdges = new THREE.LineSegments(
    new THREE.EdgesGeometry(ground.geometry),
    new THREE.LineBasicMaterial({ color: 0x00f3ff })
  );

  districtGroup.add(ground);
  districtGroup.add(groundEdges);

  scene.add(districtGroup);

  const currentKey = `${pos.x},${pos.z}`;

  const neighborOffsets = [
    [-STRIDE, 0],
    [STRIDE, 0],
    [0, -STRIDE],
    [0, STRIDE]
  ];

  neighborOffsets.forEach(([xOffset, zOffset]) => {
    const neighborX = pos.x + xOffset;
    const neighborZ = pos.z + zOffset;
    const neighborKey = `${neighborX},${neighborZ}`;

    if (existingDistricts.has(neighborKey)) {
      createRoadSegment(pos.x, pos.z, neighborX, neighborZ);
    }
  });

  existingDistricts.add(currentKey);

  if ((pos.gx === 0 && Math.abs(pos.gz) === 1) ||
      (pos.gz === 0 && Math.abs(pos.gx) === 1)) {
    createRouterRoad(pos.x, pos.z);
  }


  return districtGroup;
}



function animate() {
  controls.update();
  routerGroup.rotation.y += 0.01;

  animatingTiles.forEach(tile => {
    if (tile.userData.animating) {
      tile.position.y += (tile.userData.targetY - tile.position.y) * 0.1;

      if (Math.abs(tile.userData.targetY - tile.position.y) < 0.001) {
        tile.position.y = tile.userData.targetY;
        tile.userData.animating = false;
      }
    }
  });

  animatingRoads.forEach(road => {
    if (road.userData.animating) {
      road.scale.x += (1 - road.scale.x) * 0.1;
      road.scale.z += (1 - road.scale.z) * 0.1;

      if (Math.abs(1 - road.scale.x) < 0.001 && Math.abs(1 - road.scale.z) < 0.001) {
        road.scale.set(1, 1, 1);
        road.userData.animating = false;
      }
    }
  });

  renderer.render(scene, camera);
}

scene.add(routerGroup);

const centralTile = new THREE.Group();
centralTile.add(
  new THREE.Mesh(
    new THREE.BoxGeometry(TILE_SIZE, 0.1, TILE_SIZE),
    new THREE.MeshBasicMaterial({ color: 0x0a0a12 })
  )
);
centralTile.add(
  new THREE.LineSegments(
    new THREE.EdgesGeometry(new THREE.BoxGeometry(TILE_SIZE, 0.1, TILE_SIZE)),
    new THREE.LineBasicMaterial({ color: 0x00f3ff })
  )
);
scene.add(centralTile);

renderer.setAnimationLoop(animate);

let testDistrictCount = 0;
const testDistrictTimer = setInterval(() => {
  spawnDistrictTile(`sector_${testDistrictCount}`, testDistrictCount);
  testDistrictCount += 1;

  if (testDistrictCount >= 100) {
    clearInterval(testDistrictTimer);
  }
}, 1000);