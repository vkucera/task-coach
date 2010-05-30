//
//  TaskCategoryPickerController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 02/08/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

#import "BaseCategoryViewController.h"

@class CDTask;

@interface TaskCategoryPickerController : BaseCategoryViewController
{
	CDTask *myTask;
}

- initWithTask:(CDTask *)task;

@end
