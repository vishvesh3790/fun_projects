using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using TMPro;

public class FlappyBird3D : MonoBehaviour
{
    [Header("Bird Settings")]
    public float jumpForce = 5f;
    public float forwardSpeed = 5f;
    public float rotationSpeed = 2f;
    private Rigidbody rb;
    private bool isDead = false;

    [Header("Pipe Settings")]
    public GameObject pipePrefab;
    public float pipeSpawnInterval = 2f;
    public float pipeGapSize = 4f;
    public float pipeSpawnDistance = 20f;
    public float minHeight = -3f;
    public float maxHeight = 3f;

    [Header("UI")]
    public TextMeshProUGUI scoreText;
    public GameObject gameOverPanel;
    private int score = 0;

    [Header("Audio")]
    public AudioClip flapSound;
    public AudioClip scoreSound;
    public AudioClip deathSound;
    private AudioSource audioSource;

    void Start()
    {
        rb = GetComponent<Rigidbody>();
        audioSource = GetComponent<AudioSource>();
        StartCoroutine(SpawnPipes());
        gameOverPanel.SetActive(false);
    }

    void Update()
    {
        if (isDead)
        {
            if (Input.GetKeyDown(KeyCode.R))
            {
                RestartGame();
            }
            return;
        }

        // Bird flap
        if (Input.GetKeyDown(KeyCode.Space))
        {
            Flap();
        }

        // Rotate bird based on velocity
        float angle = Mathf.Lerp(0, 90, -rb.velocity.y / 10f);
        transform.rotation = Quaternion.Euler(angle, 0, 0);

        // Move bird forward
        Vector3 pos = transform.position;
        pos.z += forwardSpeed * Time.deltaTime;
        transform.position = pos;
    }

    void Flap()
    {
        rb.velocity = new Vector3(rb.velocity.x, jumpForce, rb.velocity.z);
        if (audioSource && flapSound)
        {
            audioSource.PlayOneShot(flapSound);
        }
    }

    IEnumerator SpawnPipes()
    {
        while (!isDead)
        {
            float randomHeight = Random.Range(minHeight, maxHeight);
            
            // Spawn bottom pipe
            GameObject bottomPipe = Instantiate(pipePrefab, 
                new Vector3(0, randomHeight - pipeGapSize/2, transform.position.z + pipeSpawnDistance), 
                Quaternion.identity);
            
            // Spawn top pipe
            GameObject topPipe = Instantiate(pipePrefab, 
                new Vector3(0, randomHeight + pipeGapSize/2, transform.position.z + pipeSpawnDistance), 
                Quaternion.Euler(180f, 0f, 0f));

            // Set pipe properties
            bottomPipe.transform.localScale = new Vector3(1f, 5f, 1f);
            topPipe.transform.localScale = new Vector3(1f, 5f, 1f);

            // Add score trigger
            BoxCollider scoreCollider = new GameObject("ScoreTrigger").AddComponent<BoxCollider>();
            scoreCollider.transform.position = new Vector3(0, 0, transform.position.z + pipeSpawnDistance);
            scoreCollider.size = new Vector3(1f, pipeGapSize, 0.1f);
            scoreCollider.isTrigger = true;
            scoreCollider.gameObject.layer = LayerMask.NameToLayer("Score");

            // Cleanup
            Destroy(bottomPipe, 10f);
            Destroy(topPipe, 10f);
            Destroy(scoreCollider.gameObject, 10f);

            yield return new WaitForSeconds(pipeSpawnInterval);
        }
    }

    void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.CompareTag("Pipe"))
        {
            GameOver();
        }
    }

    void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.layer == LayerMask.NameToLayer("Score") && !isDead)
        {
            score++;
            scoreText.text = "Score: " + score;
            if (audioSource && scoreSound)
            {
                audioSource.PlayOneShot(scoreSound);
            }
        }
    }

    void GameOver()
    {
        isDead = true;
        gameOverPanel.SetActive(true);
        if (audioSource && deathSound)
        {
            audioSource.PlayOneShot(deathSound);
        }
    }

    void RestartGame()
    {
        UnityEngine.SceneManagement.SceneManager.LoadScene(
            UnityEngine.SceneManagement.SceneManager.GetActiveScene().name
        );
    }
}
