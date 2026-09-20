import pandas as pd

def check_columns(df, required_columns):
    """
    Ensure all required columns exist in the DataFrame.
    Missing columns are added with default value 0.
    """
    # Find missing columns
    missing_cols = [col for col in required_columns if col not in df.columns]

    # Add all missing columns at once
    if missing_cols:
        df = pd.concat([df, pd.DataFrame(0, index=df.index, columns=missing_cols)], axis=1)

    # Optional: reorder columns to match required_columns
    df = df[required_columns]

    return df

# Example usage:
if __name__ == "__main__":
    # Sample DataFrame
    df = pd.DataFrame({
        'id': [1, 2],
        'dur': [0.1, 0.2],
        'spkts': [10, 20]
    })

    required_columns = ['id', 'dur', 'spkts', 'dpkts', 'sbytes', 'dbytes']

    df = check_columns(df, required_columns)
    print(df)

