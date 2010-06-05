//
//  ParentTaskViewController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 05/06/10.
//  Copyright 2010 Jérôme Laheurte. All rights reserved.
//

#import "TaskViewController.h"
#import "CDTask.h"

@interface ParentTaskViewController : TaskViewController
{
	CDTask *parent;
}

- initWithCategoryController:(CategoryViewController *)controller edit:(BOOL)edit parent:(CDTask *)parent;

@end
