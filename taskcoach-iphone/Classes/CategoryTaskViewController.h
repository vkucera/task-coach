//
//  CategoryTaskViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 30/05/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskViewController.h"
#import "CDCategory.h"

@interface CategoryTaskViewController : TaskViewController
{
	CDCategory *category;
}

- initWithCategoryController:(CategoryViewController *)controller edit:(BOOL)edit category:(CDCategory *)category;

- (void)setCategory:(CDCategory *)category;

@end
