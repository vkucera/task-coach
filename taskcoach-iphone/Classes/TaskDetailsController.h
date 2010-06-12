//
//  TaskDetailsController.h
//  TaskCoach
//
//  Created by Jérôme Laheurte on 19/01/09.
//  Copyright 2009 Jérôme Laheurte. See COPYING for details.
//

#import <UIKit/UIKit.h>

@class CDTask;

@interface TaskDetailsController : UITabBarController <UITabBarControllerDelegate>
{
	CDTask *task;
}

- initWithTask:(CDTask *)task;
- initWithTask:(CDTask *)task tabIndex:(NSInteger)index;

@end
