//
//  BaseCategoryViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 02/08/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

@class CDCategory;
@class BadgedCell;

@interface BaseCategoryViewController : UITableViewController
{
	NSMutableArray *categories;
	NSMutableDictionary *indentations;
}

- (void)loadCategories;

- (void)fillCell:(BadgedCell *)cell forCategory:(CDCategory *)category;

@end
