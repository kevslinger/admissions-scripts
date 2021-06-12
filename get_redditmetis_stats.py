from selenium.common.exceptions import NoSuchElementException
import re


def get_stats(driver):
    stats = []
    try:
        # Comment Count
        #statname = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[1]/div/div[1]/div/div[2]/div/p').text
        comment_count = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[1]/div/div[1]/div/div[1]/div/p').text
        stats.append(f"{comment_count}")
        # Comment Karma
        #statname = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[1]/div/div[3]/div/div[2]/div/p').text
        #comment_karma = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[1]/div/div[3]/div/div[1]/div/p').text
        #stats.append(f"{comment_karma}")
        # Avg Karma per comment
        #statname = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[1]/div/div[4]/div/div[2]/div/p').text
        avg_comment_karma = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[1]/div/div[4]/div/div[1]/div/p').text
        stats.append(f"{avg_comment_karma}")
        # Wholesomeness
        wholesomeness = driver.find_element_by_xpath('//*[@id="sentiment-right"]').text
        stats.append(f"{wholesomeness}")
        # Subreddits
        subreddit_comments = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[3]/div[2]').text.split('\n')
        subreddit_submissions = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[5]/div/div[2]/div[3]').text.split('\n')
        subreddits = set([sub for sub in subreddit_submissions + subreddit_comments if re.search('r\/[a-zA-Z]+', sub)])
        stats.append(f"{', '.join(subreddits)}")
        # Least Wholesome COMMENT
        least_wholesome_comment = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[1]/div/div[2]/div[1]/div/div[15]/div/div[1]/span/p').text
        least_wholesome_sub = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[1]/div/div[2]/div[1]/div/div[15]/div/div[2]/p[1]/a').text
        least_wholesome_karma = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[1]/div/div[2]/div[1]/div/div[15]/div/div[2]/p[2]/span[1]').text
        least_wholesome_link = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[1]/div/div[2]/div[1]/div/div[15]/div/div[2]/p[2]/span[3]/a').get_attribute('href')
        stats.append(f"\"{least_wholesome_comment}\" from {least_wholesome_sub} with {least_wholesome_karma} karma")
        stats.append(f"=HYPERLINK(\"{least_wholesome_link}\", \"LINK\")")
        # Most Downvoted Comment
        most_downvoted_comment = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[2]/div[4]/div[1]/span').text
        most_downvoted_comment_sub = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[2]/div[4]/div[2]/p[1]/a').text
        num_downvotes_comment = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[2]/div[4]/div[2]/p[2]/span[1]').text
        most_downvoted_comment_link = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[4]/div/div[2]/div[2]/div[4]/div[2]/p[2]/span[3]/a').get_attribute('href')
        stats.append(f"\"{most_downvoted_comment}\" from {most_downvoted_comment_sub} with {num_downvotes_comment} karma")
        stats.append(f"=HYPERLINK(\"{most_downvoted_comment_link}\", \"LINK\")")
        # Most Downvoted POST
        most_downvoted_post = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[5]/div/div[2]/div[2]/div[4]/div[1]/p/span').text
        most_downvoted_post_sub = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[5]/div/div[2]/div[2]/div[4]/div[2]/p[1]/a').text
        num_downvotes_post = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[5]/div/div[2]/div[2]/div[4]/div[2]/p[2]/span[1]').text
        num_downvotes_link = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[5]/div/div[2]/div[2]/div[4]/div[2]/p[2]/span[3]/a').get_attribute('href')
        #print(dir(num_downvotes_link))
        #print(f"Most downvoted post: {most_downvoted_post} from {most_downvoted_post_sub} with {num_downvotes_post} karma LINK {num_downvotes_link}")
        stats.append(f"Most downvoted post: \"{most_downvoted_post}\" from {most_downvoted_post_sub} with {num_downvotes_post} karma")
        stats.append(f"=HYPERLINK(\"{num_downvotes_link}\", \"LINK\")")
        # Frequently Used Words:
        wordcloud = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div/div/div[2]/div[6]/div/div[2]/div[2]/div/div[3]/div/table').text.split('\n')
        stats.append(f"{','.join([word for word in wordcloud[2:] if word.isalpha()])}")
        return stats
    except NoSuchElementException:
        return 0


