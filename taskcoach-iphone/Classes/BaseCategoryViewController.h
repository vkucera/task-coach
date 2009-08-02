//
//  BaseCategoryViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 02/08/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import <UIKit/UIKit.h>

@class Category;

@interface BaseCategoryViewController : UITableViewController
{
	NSMutableArray *categories;
}

- (void)loadCategories;

- (void)fillCell:(UITableViewCell *)cell forCategory:(Category *)category;

@end
